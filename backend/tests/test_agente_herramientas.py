from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.agente.herramientas import DESCRIPCIONES, construir_herramientas, declaraciones
from app.indicadores import calcular_resumen
from app.models import Producto, Venta
from app.seed import seed_demo_data


def test_solo_se_declaran_las_tres_herramientas_de_lectura_sin_parametros():
    declaradas = {d.name: d for d in declaraciones()}

    assert set(declaradas) == {
        "consultar_resumen_ventas",
        "consultar_ventas_por_producto",
        "consultar_ventas_por_categoria",
    }
    assert all(d.parameters is None for d in declaradas.values())
    assert set(construir_herramientas(None)) == set(DESCRIPCIONES)


def test_herramienta_resumen_devuelve_los_datos_de_sqlite(session: Session):
    seed_demo_data(session)

    datos = construir_herramientas(session)["consultar_resumen_ventas"]()
    resumen = calcular_resumen(session)

    assert datos["numero_ventas"] == 50
    assert datos["ingresos_totales"] == float(resumen.ingresos_totales)
    assert datos["cantidad_vendida"] == resumen.cantidad_vendida
    assert datos["ticket_promedio"] == float(resumen.ticket_promedio)


def test_herramienta_por_producto_incluye_productos_sin_ventas(session: Session):
    seed_demo_data(session)
    session.add(Producto(nombre="Producto sin ventas", categoria="Oficina", precio=10))
    session.commit()

    productos = construir_herramientas(session)["consultar_ventas_por_producto"]()["productos"]

    assert len(productos) == 11
    sin_ventas = next(p for p in productos if p["nombre"] == "Producto sin ventas")
    assert sin_ventas["cantidad_vendida"] == 0
    assert sin_ventas["ingresos"] == 0.0
    ingresos = [p["ingresos"] for p in productos]
    assert ingresos == sorted(ingresos, reverse=True)


def test_herramienta_por_producto_suma_coincide_con_total(session: Session):
    seed_demo_data(session)

    productos = construir_herramientas(session)["consultar_ventas_por_producto"]()["productos"]
    ventas = session.scalars(select(Venta)).all()

    assert round(sum(p["ingresos"] for p in productos), 2) == float(sum(v.cantidad * v.precio_unitario for v in ventas))
    assert sum(p["cantidad_vendida"] for p in productos) == sum(v.cantidad for v in ventas)


def test_herramienta_por_categoria_coincide_con_indicadores(session: Session):
    seed_demo_data(session)

    categorias = construir_herramientas(session)["consultar_ventas_por_categoria"]()["categorias"]
    esperado = {c.categoria: float(c.ingresos) for c in calcular_resumen(session).ventas_por_categoria}

    assert {c["categoria"]: c["ingresos"] for c in categorias} == esperado


def test_las_herramientas_no_modifican_registros(session: Session):
    seed_demo_data(session)
    antes = (session.scalar(select(func.count(Venta.id))), session.scalar(select(func.count(Producto.id))))

    herramientas = construir_herramientas(session)
    for funcion in herramientas.values():
        funcion()

    despues = (session.scalar(select(func.count(Venta.id))), session.scalar(select(func.count(Producto.id))))
    assert antes == despues == (50, 10)
