"""Datos de demostración reproducibles. Solo se generan a partir de este archivo."""

import random
from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from app.config import DATABASE_URL
from app.models import Base, Producto, Venta

SEMILLA = 2026
NUMERO_VENTAS = 50
FECHA_INICIO = date(2026, 1, 1)
DIAS_PERIODO = 90

PRODUCTOS_DEMO = [
    ("Auriculares inalámbricos", "Electrónica", Decimal("59.90")),
    ("Teclado mecánico", "Electrónica", Decimal("89.50")),
    ("Monitor 24 pulgadas", "Electrónica", Decimal("179.00")),
    ("Lámpara LED", "Hogar", Decimal("25.75")),
    ("Cafetera de goteo", "Hogar", Decimal("39.99")),
    ("Silla ergonómica", "Oficina", Decimal("149.00")),
    ("Cuaderno A5", "Oficina", Decimal("3.50")),
    ("Caja de bolígrafos", "Oficina", Decimal("6.20")),
    ("Café molido 250 g", "Alimentos", Decimal("7.80")),
    ("Galletas integrales", "Alimentos", Decimal("2.95")),
]


def seed_demo_data(session: Session) -> dict[str, int]:
    """Inserta productos y 50 ventas si la base de datos está vacía. Es idempotente."""
    if session.scalar(select(func.count(Producto.id))) > 0:
        return {"productos": 0, "ventas": 0}

    productos = [
        Producto(nombre=nombre, categoria=categoria, precio=precio)
        for nombre, categoria, precio in PRODUCTOS_DEMO
    ]
    session.add_all(productos)
    session.flush()

    generador = random.Random(SEMILLA)
    for _ in range(NUMERO_VENTAS):
        producto = generador.choice(productos)
        session.add(
            Venta(
                producto_id=producto.id,
                cantidad=generador.randint(1, 5),
                precio_unitario=producto.precio,
                fecha=FECHA_INICIO + timedelta(days=generador.randrange(DIAS_PERIODO)),
            )
        )
    session.commit()
    return {"productos": len(productos), "ventas": NUMERO_VENTAS}


if __name__ == "__main__":
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        print(seed_demo_data(session))
