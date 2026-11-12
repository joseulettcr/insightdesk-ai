import httpx
import pytest
from fastapi.testclient import TestClient
from google.genai import errors

from app.main import create_app
from app.models import Base
from app.seed import seed_demo_data
from sqlalchemy.orm import Session
from tests.gemini_falso import ClienteFalso, respuesta_llamada, respuesta_texto


@pytest.fixture
def cliente_api(database_url: str):
    def construir(*secuencia):
        cliente = ClienteFalso(*secuencia)
        application = create_app(database_url, cliente_gemini=cliente)
        Base.metadata.create_all(application.state.engine)
        with application.state.session_factory() as session:
            seed_demo_data(session)
        return TestClient(application), cliente, application

    return construir


def test_chat_responde_con_texto_y_herramientas_usadas(cliente_api):
    client, cliente, app = cliente_api(
        respuesta_llamada("consultar_resumen_ventas"),
        respuesta_texto("Tienes 50 ventas registradas."),
    )
    with client:
        respuesta = client.post("/api/agente/chat", json={"mensaje": "¿Cuántas ventas tengo?"})

    assert respuesta.status_code == 200
    assert respuesta.json() == {
        "respuesta": "Tienes 50 ventas registradas.",
        "herramientas_usadas": ["consultar_resumen_ventas"],
    }
    app.state.engine.dispose()


def test_chat_sin_clave_configurada_devuelve_503(database_url: str):
    application = create_app(database_url, cliente_gemini=None)
    Base.metadata.create_all(application.state.engine)

    with TestClient(application) as client:
        respuesta = client.post("/api/agente/chat", json={"mensaje": "Hola"})

    assert respuesta.status_code == 503
    assert respuesta.json() == {"detail": "El asistente no está configurado en el servidor."}
    application.state.engine.dispose()


@pytest.mark.parametrize("mensaje", ["", "   ", "x" * 1001])
def test_chat_rechaza_mensajes_invalidos(cliente_api, mensaje):
    client, cliente, app = cliente_api()
    with client:
        respuesta = client.post("/api/agente/chat", json={"mensaje": mensaje})

    assert respuesta.status_code == 422
    assert cliente.llamadas == []
    app.state.engine.dispose()


def test_chat_exige_el_campo_mensaje(cliente_api):
    client, _, app = cliente_api()
    with client:
        assert client.post("/api/agente/chat", json={}).status_code == 422
        assert client.post("/api/agente/chat", json={"pregunta": "Hola"}).status_code == 422
    app.state.engine.dispose()


@pytest.mark.parametrize(
    ("excepcion", "codigo_http"),
    [
        (errors.ClientError(429, {"error": {"code": 429, "message": "cuota", "status": "RESOURCE_EXHAUSTED"}}, None), 429),
        (errors.ServerError(504, {"error": {"code": 504, "message": "tarde", "status": "DEADLINE_EXCEEDED"}}, None), 504),
        (httpx.ReadTimeout("tiempo agotado"), 504),
        (errors.ClientError(401, {"error": {"code": 401, "message": "clave", "status": "UNAUTHENTICATED"}}, None), 502),
    ],
)
def test_chat_traduce_errores_de_gemini(cliente_api, excepcion, codigo_http):
    client, _, app = cliente_api(excepcion)
    with client:
        respuesta = client.post("/api/agente/chat", json={"mensaje": "Hola"})

    assert respuesta.status_code == codigo_http
    assert "detail" in respuesta.json()
    app.state.engine.dispose()


def test_chat_con_respuesta_vacia_devuelve_502(cliente_api):
    from tests.gemini_falso import respuesta_vacia

    client, _, app = cliente_api(respuesta_vacia())
    with client:
        respuesta = client.post("/api/agente/chat", json={"mensaje": "Hola"})

    assert respuesta.status_code == 502
    app.state.engine.dispose()


def test_la_clave_de_gemini_no_aparece_en_las_respuestas(cliente_api):
    secreto = "AIzaSy-CLAVE-SECRETA-DE-PRUEBA"
    client, _, app = cliente_api(
        errors.ClientError(401, {"error": {"code": 401, "message": secreto, "status": "UNAUTHENTICATED"}}, None),
    )
    with client:
        respuesta = client.post("/api/agente/chat", json={"mensaje": "Hola"})
        esquema = client.get("/openapi.json").text

    assert secreto not in respuesta.text
    assert secreto not in esquema
    app.state.engine.dispose()


def test_cliente_gemini_se_crea_solo_con_la_variable_de_entorno(monkeypatch):
    from app.agente.gemini import crear_cliente_desde_entorno

    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    assert crear_cliente_desde_entorno() is None

    monkeypatch.setenv("GEMINI_API_KEY", "   ")
    assert crear_cliente_desde_entorno() is None
