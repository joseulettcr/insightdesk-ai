from decimal import Decimal

from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session, sessionmaker

from app.models import Base, Producto, Venta
from app.seed import NUMERO_VENTAS, PRODUCTOS_DEMO, seed_demo_data


def test_seed_inserta_productos_y_50_ventas(session: Session):
    resultado = seed_demo_data(session)

    assert resultado == {"productos": len(PRODUCTOS_DEMO), "ventas": NUMERO_VENTAS}
    assert session.scalar(select(func.count(Producto.id))) == 10
    assert session.scalar(select(func.count(Venta.id))) == 50


def test_seed_es_idempotente(session: Session):
    seed_demo_data(session)

    segunda = seed_demo_data(session)

    assert segunda == {"productos": 0, "ventas": 0}
    assert session.scalar(select(func.count(Venta.id))) == 50


def test_seed_es_reproducible(tmp_path):
    def generar(nombre: str) -> list[tuple]:
        engine = create_engine(f"sqlite:///{tmp_path / nombre}")
        Base.metadata.create_all(engine)
        with sessionmaker(bind=engine)() as session:
            seed_demo_data(session)
            filas = [
                (v.producto_id, v.cantidad, v.precio_unitario, v.fecha)
                for v in session.scalars(select(Venta).order_by(Venta.id))
            ]
        engine.dispose()
        return filas

    assert generar("a.db") == generar("b.db")


def test_precios_del_seed_coinciden_con_catalogo(session: Session):
    seed_demo_data(session)

    precios = {p.nombre: p.precio for p in session.scalars(select(Producto))}

    for nombre, _, precio in PRODUCTOS_DEMO:
        assert precios[nombre] == precio
        assert isinstance(precios[nombre], Decimal)
