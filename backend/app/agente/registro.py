import logging
import os
import threading
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

# Por defecto, log.md en la raíz del proyecto (backend/app/agente/registro.py -> insightdesk-ai/).
# INSIGHTDESK_LOG_PATH permite cambiarla (las pruebas la apuntan a un directorio temporal).
RUTA_LOG_POR_DEFECTO = Path(__file__).resolve().parents[3] / "log.md"


def ruta_log() -> Path:
    return Path(os.getenv("INSIGHTDESK_LOG_PATH") or RUTA_LOG_POR_DEFECTO)

CABECERA = (
    "# Log de errores del Asistente\n\n"
    "| Fecha | Código | Tipo | Detalle |\n"
    "|---|---|---|---|\n"
)
_cerrojo = threading.Lock()


def registrar(codigo: int, tipo: str, detalle: str) -> None:
    """Añade una línea a log.md. Solo recibe mensajes fijos: nunca claves ni texto del usuario.

    Un fallo al escribir el log no debe afectar a la petición del usuario.
    """
    try:
        fila = f"| {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | {codigo} | {tipo} | {detalle} |\n"
        with _cerrojo:
            ruta = ruta_log()
            nuevo = not ruta.exists()
            with ruta.open("a", encoding="utf-8") as archivo:
                if nuevo:
                    archivo.write(CABECERA)
                archivo.write(fila)
    except OSError:
        logger.warning("No se pudo escribir en log.md")
