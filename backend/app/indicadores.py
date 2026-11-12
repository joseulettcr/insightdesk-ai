from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

from sqlalchemy import Integer, func, select
from sqlalchemy.orm import Session

from app.models import Producto, Venta


@dataclass(frozen=True)
class ResumenCategoria:
    categoria: str
    cantidad_vendida: int
    ingresos: Decimal


@dataclass(frozen=True)
class Resumen:
    ingresos_totales: Decimal
    cantidad_vendida: int
    numero_ventas: int
    ticket_promedio: Decimal
    ventas_por_categoria: list[ResumenCategoria]


def _ingreso_linea():
    # cantidad * precio_unitario en céntimos; la suma se hace en SQL sobre enteros.
    return func.sum(Venta.cantidad * Venta.precio_unitario, type_=Integer)


def _desde_centimos(centimos: int | None) -> Decimal:
    return (Decimal(centimos or 0) / 100).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def calcular_resumen(session: Session) -> Resumen:
    total = session.execute(
        select(
            _ingreso_linea(),
            func.coalesce(func.sum(Venta.cantidad), 0),
            func.count(Venta.id),
        )
    ).one()
    centimos, cantidad, numero = total
    ingresos = _desde_centimos(centimos)
    ticket = (ingresos / numero).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP) if numero else Decimal("0.00")

    filas = session.execute(
        select(
            Producto.categoria,
            func.sum(Venta.cantidad),
            _ingreso_linea(),
        )
        .select_from(Venta)
        .join(Producto, Producto.id == Venta.producto_id)
        .group_by(Producto.categoria)
        .order_by(Producto.categoria)
    ).all()

    return Resumen(
        ingresos_totales=ingresos,
        cantidad_vendida=int(cantidad),
        numero_ventas=int(numero),
        ticket_promedio=ticket,
        ventas_por_categoria=[
            ResumenCategoria(
                categoria=categoria,
                cantidad_vendida=int(unidades),
                ingresos=_desde_centimos(lineas),
            )
            for categoria, unidades, lineas in filas
        ],
    )


@dataclass(frozen=True)
class ResumenProducto:
    producto_id: int
    nombre: str
    categoria: str
    cantidad_vendida: int
    ingresos: Decimal


def ventas_por_producto(session: Session) -> list[ResumenProducto]:
    """Todos los productos del catálogo, incluidos los que no tienen ventas (valores a cero)."""
    lineas = {
        producto_id: (int(unidades), centimos)
        for producto_id, unidades, centimos in session.execute(
            select(Venta.producto_id, func.sum(Venta.cantidad), _ingreso_linea()).group_by(Venta.producto_id)
        ).all()
    }
    resumenes = []
    for producto in session.scalars(select(Producto).order_by(Producto.id)).all():
        unidades, centimos = lineas.get(producto.id, (0, None))
        resumenes.append(
            ResumenProducto(
                producto_id=producto.id,
                nombre=producto.nombre,
                categoria=producto.categoria,
                cantidad_vendida=unidades,
                ingresos=_desde_centimos(centimos),
            )
        )
    return resumenes
