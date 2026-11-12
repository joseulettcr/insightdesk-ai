import httpx
import pytest
from google.genai import errors
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.agente.errores import AgenteError
from app.agente.herramientas import construir_herramientas
from app.agente.servicio import MAX_TURNOS, responder
from app.indicadores import calcular_resumen
from app.models import Venta
from app.seed import seed_demo_data
from tests.gemini_falso import (
    ClienteFalso,
    respuesta_llamada,
    respuesta_texto,
    respuesta_vacia,
    resultados_enviados,
)

MODELO = "modelo-de-prueba"


def _herramientas(session: Session):
    seed_demo_data(session)
    return construir_herramientas(session)


def test_agente_llama_a_la_herramienta_y_usa_datos_reales(session: Session):
    herramientas = _herramientas(session)
    cliente = ClienteFalso(
        respuesta_llamada("consultar_resumen_ventas"),
        respuesta_texto("Hay 50 ventas registradas."),
    )

    resultado = responder(cliente, herramientas, "¿Cuántas ventas hay?", MODELO)

    assert resultado.texto == "Hay 50 ventas registradas."
    assert resultado.herramientas_usadas == ["consultar_resumen_ventas"]
    datos = resultados_enviados(cliente)[0]["resultado"]
    assert datos["numero_ventas"] == 50
    assert datos["ingresos_totales"] == float(calcular_resumen(session).ingresos_totales)


def test_agente_puede_encadenar_varias_herramientas(session: Session):
    herramientas = _herramientas(session)
    cliente = ClienteFalso(
        respuesta_llamada("consultar_ventas_por_producto"),
        respuesta_llamada("consultar_ventas_por_categoria"),
        respuesta_texto("Recomendación basada en los datos."),
    )

    resultado = responder(cliente, herramientas, "¿Qué conviene impulsar?", MODELO)

    assert resultado.herramientas_usadas == ["consultar_ventas_por_producto", "consultar_ventas_por_categoria"]
    assert len(cliente.llamadas) == 3


def test_agente_responde_sin_herramientas_si_el_modelo_no_las_necesita(session: Session):
    herramientas = _herramientas(session)
    cliente = ClienteFalso(respuesta_texto("Hola."))

    resultado = responder(cliente, herramientas, "Hola", MODELO)

    assert resultado.texto == "Hola."
    assert resultado.herramientas_usadas == []


def test_herramienta_inexistente_no_se_ejecuta_y_no_rompe_la_respuesta(session: Session):
    herramientas = _herramientas(session)
    cliente = ClienteFalso(
        respuesta_llamada("ejecutar_sql", {"sql": "DROP TABLE ventas"}),
        respuesta_texto("No puedo ejecutar esa consulta."),
    )

    resultado = responder(cliente, herramientas, "Borra las ventas", MODELO)

    assert resultado.herramientas_usadas == []
    assert resultados_enviados(cliente)[0]["resultado"] == {"error": "La herramienta solicitada no existe."}
    assert session.scalar(select(func.count(Venta.id))) == 50


def test_fallo_de_herramienta_se_devuelve_como_error_controlado(session: Session):
    herramientas = _herramientas(session)

    def herramienta_rota() -> dict:
        raise RuntimeError("fallo interno con detalle sensible")

    herramientas["consultar_resumen_ventas"] = herramienta_rota
    cliente = ClienteFalso(
        respuesta_llamada("consultar_resumen_ventas"),
        respuesta_texto("No he podido consultar los datos."),
    )

    resultado = responder(cliente, herramientas, "Resumen", MODELO)

    assert resultado.texto == "No he podido consultar los datos."
    assert resultados_enviados(cliente)[0]["resultado"] == {"error": "No se pudieron consultar los datos."}
    assert "sensible" not in str(resultados_enviados(cliente))


def test_respuesta_vacia_produce_error_502(session: Session):
    herramientas = _herramientas(session)

    with pytest.raises(AgenteError) as info:
        responder(ClienteFalso(respuesta_vacia()), herramientas, "Hola", MODELO)

    assert info.value.status_code == 502
    assert "no devolvió una respuesta" in info.value.detail


def test_texto_en_blanco_produce_error_502(session: Session):
    herramientas = _herramientas(session)

    with pytest.raises(AgenteError) as info:
        responder(ClienteFalso(respuesta_texto("   ")), herramientas, "Hola", MODELO)

    assert info.value.status_code == 502


def test_limite_de_turnos_evita_bucles_infinitos(session: Session):
    herramientas = _herramientas(session)
    cliente = ClienteFalso(*[respuesta_llamada("consultar_resumen_ventas") for _ in range(MAX_TURNOS)])

    with pytest.raises(AgenteError) as info:
        responder(cliente, herramientas, "Bucle", MODELO)

    assert info.value.status_code == 502
    assert len(cliente.llamadas) == MAX_TURNOS


@pytest.mark.parametrize(
    ("excepcion", "codigo_http"),
    [
        (errors.ClientError(401, {"error": {"code": 401, "message": "clave inválida", "status": "UNAUTHENTICATED"}}, None), 502),
        (errors.ClientError(403, {"error": {"code": 403, "message": "permiso", "status": "PERMISSION_DENIED"}}, None), 502),
        (errors.ClientError(429, {"error": {"code": 429, "message": "cuota", "status": "RESOURCE_EXHAUSTED"}}, None), 429),
        (errors.ServerError(504, {"error": {"code": 504, "message": "deadline", "status": "DEADLINE_EXCEEDED"}}, None), 504),
        (errors.ServerError(500, {"error": {"code": 500, "message": "interno", "status": "INTERNAL"}}, None), 502),
        (httpx.ReadTimeout("tiempo agotado"), 504),
        (TimeoutError("tiempo agotado"), 504),
        (ValueError("algo inesperado"), 502),
    ],
)
def test_errores_de_gemini_se_traducen_a_codigos_http(session: Session, excepcion, codigo_http):
    herramientas = _herramientas(session)

    with pytest.raises(AgenteError) as info:
        responder(ClienteFalso(excepcion), herramientas, "Pregunta", MODELO)

    assert info.value.status_code == codigo_http


def test_mensajes_de_error_no_filtran_detalles_del_proveedor(session: Session):
    herramientas = _herramientas(session)
    secreto = "AIzaSy-CLAVE-SECRETA-DE-PRUEBA"
    excepcion = errors.ClientError(401, {"error": {"code": 401, "message": secreto, "status": "UNAUTHENTICATED"}}, None)

    with pytest.raises(AgenteError) as info:
        responder(ClienteFalso(excepcion), herramientas, "Pregunta", MODELO)

    assert secreto not in info.value.detail
    assert secreto not in str(info.value)


def test_la_configuracion_envia_la_instruccion_y_las_herramientas(session: Session):
    herramientas = _herramientas(session)
    cliente = ClienteFalso(respuesta_texto("ok"))

    responder(cliente, herramientas, "Hola", MODELO)

    config = cliente.llamadas[0]["config"]
    assert cliente.llamadas[0]["model"] == MODELO
    assert "Nunca inventes cifras" in config.system_instruction
    nombres = {d.name for d in config.tools[0].function_declarations}
    assert nombres == {"consultar_resumen_ventas", "consultar_ventas_por_producto", "consultar_ventas_por_categoria"}
