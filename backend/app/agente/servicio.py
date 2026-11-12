import logging
from collections.abc import Callable
from dataclasses import dataclass, field

from google.genai import types

from app.agente.errores import AgenteError
from app.agente.gemini import traducir_error
from app.agente.herramientas import declaraciones
from app.agente.registro import registrar

logger = logging.getLogger(__name__)

MAX_TURNOS = 6
TEMPERATURA = 0.2

INSTRUCCION_SISTEMA = """Eres el asistente de análisis comercial de InsightDesk AI. Responde siempre en español.
- Para cualquier cifra usa las herramientas disponibles. Nunca inventes cifras.
- Si una herramienta no devuelve datos suficientes, indícalo explícitamente.
- Cuando recomiendes acciones comerciales, fundaméntalas en los datos obtenidos y explica brevemente el motivo.
- Solo consultas información; no puedes modificar datos."""


@dataclass(frozen=True)
class RespuestaAgente:
    texto: str
    herramientas_usadas: list[str] = field(default_factory=list)


def _ejecutar_herramienta(llamada, herramientas: dict[str, Callable[[], dict]], usadas: list[str]) -> types.Part:
    nombre = llamada.name
    funcion = herramientas.get(nombre)
    if funcion is None:
        logger.warning("El modelo solicitó una herramienta no registrada")
        registrar(200, "Herramienta no registrada", "El modelo solicitó una función inexistente.")
        resultado = {"error": "La herramienta solicitada no existe."}
    else:
        usadas.append(nombre)
        try:
            resultado = funcion()
        except Exception:
            logger.exception("Fallo al ejecutar la herramienta %s", nombre)
            registrar(200, "Herramienta fallida", f"Fallo al ejecutar {nombre}.")
            resultado = {"error": "No se pudieron consultar los datos."}
    return types.Part.from_function_response(name=nombre, response={"resultado": resultado})


def responder(cliente, herramientas: dict[str, Callable[[], dict]], pregunta: str, modelo: str) -> RespuestaAgente:
    configuracion = types.GenerateContentConfig(
        system_instruction=INSTRUCCION_SISTEMA,
        tools=[types.Tool(function_declarations=declaraciones())],
        temperature=TEMPERATURA,
    )
    conversacion = [types.Content(role="user", parts=[types.Part(text=pregunta)])]
    usadas: list[str] = []

    try:
        for _ in range(MAX_TURNOS):
            respuesta = cliente.models.generate_content(model=modelo, contents=conversacion, config=configuracion)
            llamadas = respuesta.function_calls or []

            if not llamadas:
                texto = (respuesta.text or "").strip()
                if not texto:
                    registrar(502, "Respuesta vacía", "El modelo no devolvió texto.")
                    raise AgenteError(502, "El modelo no devolvió una respuesta.")
                return RespuestaAgente(texto=texto, herramientas_usadas=usadas)

            contenido_modelo = respuesta.candidates[0].content if respuesta.candidates else None
            if contenido_modelo is None:
                registrar(502, "Respuesta vacía", "El modelo no devolvió contenido.")
                raise AgenteError(502, "El modelo no devolvió una respuesta.")
            conversacion.append(contenido_modelo)
            conversacion.append(
                types.Content(
                    role="user",
                    parts=[_ejecutar_herramienta(llamada, herramientas, usadas) for llamada in llamadas],
                )
            )
    except AgenteError:
        raise
    except Exception as exc:
        raise traducir_error(exc) from None

    registrar(502, "Límite de turnos", f"Se superaron {MAX_TURNOS} turnos de herramientas.")
    raise AgenteError(502, "El agente superó el número máximo de consultas.")
