import logging
import os

import httpx
from google import genai
from google.genai import errors, types

from app.agente.errores import AgenteError

logger = logging.getLogger(__name__)

TIMEOUT_MS = 30_000


def crear_cliente_desde_entorno() -> genai.Client | None:
    """Crea el cliente de Gemini con GEMINI_API_KEY. Devuelve None si la clave no está definida."""
    clave = os.getenv("GEMINI_API_KEY", "").strip()
    if not clave:
        return None
    return genai.Client(api_key=clave, http_options=types.HttpOptions(timeout=TIMEOUT_MS))


def traducir_error(exc: Exception) -> AgenteError:
    """Convierte errores del SDK en respuestas HTTP seguras. Nunca incluye el mensaje original."""
    if isinstance(exc, (httpx.TimeoutException, TimeoutError)):
        logger.warning("Timeout al consultar Gemini")
        return AgenteError(504, "El servicio de IA no respondió a tiempo. Inténtalo de nuevo.")

    if isinstance(exc, errors.APIError):
        logger.warning("Error de la API de Gemini: código %s", exc.code)
        if exc.code in (401, 403):
            return AgenteError(502, "Autenticación con el servicio de IA fallida. Revisa la configuración del servidor.")
        if exc.code == 429:
            return AgenteError(429, "Se ha agotado la cuota del servicio de IA. Inténtalo más tarde.")
        if exc.code == 504:
            return AgenteError(504, "El servicio de IA no respondió a tiempo. Inténtalo de nuevo.")
        return AgenteError(502, "Error del servicio de IA.")

    logger.error("Error inesperado al consultar Gemini: %s", type(exc).__name__)
    return AgenteError(502, "Error inesperado al consultar el servicio de IA.")
