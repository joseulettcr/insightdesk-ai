"""Herramientas de solo lectura que el agente puede invocar mediante function calling.

Ninguna herramienta recibe parámetros del modelo ni ejecuta SQL arbitrario:
todas usan consultas SQLAlchemy fijas sobre la sesión de la petición.
"""

from collections.abc import Callable
from decimal import Decimal

from google.genai import types
from sqlalchemy.orm import Session

from app.indicadores import calcular_resumen, ventas_por_producto

DESCRIPCIONES = {
    "consultar_resumen_ventas": (
        "Devuelve el resumen global de ventas: ingresos totales, unidades vendidas, número de ventas y ticket promedio."
    ),
    "consultar_ventas_por_producto": (
        "Devuelve, para cada producto del catálogo, las unidades vendidas e ingresos. Incluye los productos sin ventas."
    ),
    "consultar_ventas_por_categoria": (
        "Devuelve las unidades vendidas e ingresos agrupados por categoría de producto."
    ),
}


def _numero(valor: Decimal) -> float:
    return float(valor)


def construir_herramientas(session: Session) -> dict[str, Callable[[], dict]]:
    def consultar_resumen_ventas() -> dict:
        resumen = calcular_resumen(session)
        return {
            "ingresos_totales": _numero(resumen.ingresos_totales),
            "cantidad_vendida": resumen.cantidad_vendida,
            "numero_ventas": resumen.numero_ventas,
            "ticket_promedio": _numero(resumen.ticket_promedio),
        }

    def consultar_ventas_por_producto() -> dict:
        productos = sorted(ventas_por_producto(session), key=lambda p: p.ingresos, reverse=True)
        return {
            "productos": [
                {
                    "nombre": p.nombre,
                    "categoria": p.categoria,
                    "cantidad_vendida": p.cantidad_vendida,
                    "ingresos": _numero(p.ingresos),
                }
                for p in productos
            ]
        }

    def consultar_ventas_por_categoria() -> dict:
        resumen = calcular_resumen(session)
        return {
            "categorias": [
                {
                    "categoria": c.categoria,
                    "cantidad_vendida": c.cantidad_vendida,
                    "ingresos": _numero(c.ingresos),
                }
                for c in resumen.ventas_por_categoria
            ]
        }

    return {
        "consultar_resumen_ventas": consultar_resumen_ventas,
        "consultar_ventas_por_producto": consultar_ventas_por_producto,
        "consultar_ventas_por_categoria": consultar_ventas_por_categoria,
    }


def declaraciones() -> list[types.FunctionDeclaration]:
    """Declaraciones para Gemini. Ninguna herramienta tiene parámetros."""
    return [types.FunctionDeclaration(name=nombre, description=descripcion) for nombre, descripcion in DESCRIPCIONES.items()]
