from collections import defaultdict
from datetime import date
from decimal import Decimal

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.indicadores import calcular_resumen
from app.models import Producto, Venta


def _recalcular_en_python(session: Session) -> dict:
    """Cálculo independiente de SQL: recorre cada venta y producto en memoria."""
    productos = {p.id: p for p in session.scalars(select(Producto))}
    ventas = list(session.scalars(select(Venta)))

    ingresos = sum(v.cantidad * v.precio_unitario for v in ventas)
    cantidad = sum(v.cantidad for v in ventas)
    por_categoria = defaultdict(lambda: {"cantidad_vendida": 0, "ingresos": Decimal("0")})
    for v in ventas:
        categoria = productos[v.producto_id].categoria
        por_categoria[categoria]["cantidad_vendida"] += v.cantidad
        por_categoria[categoria]["ingresos"] += v.cantidad * v.precio_unitario

    return {
        "ingresos_totales": ingresos,
        "cantidad_vendida": cantidad,
        "numero_ventas": len(ventas),
        "ticket_promedio": (ingresos / len(ventas)).quantize(Decimal("0.01")),
        "ventas_por_categoria": dict(sorted(por_categoria.items())),
    }


def test_resumen_vacio_devuelve_ceros(session: Session):
    resumen = calcular_resumen(session)

    assert resumen.ingresos_totales == Decimal("0.00")
    assert resumen.cantidad_vendida == 0
    assert resumen.numero_ventas == 0
    assert resumen.ticket_promedio == Decimal("0.00")
    assert resumen.ventas_por_categoria == []


def test_indicadores_con_valores_calculados_a_mano(session: Session):
    lampara = Producto(nombre="Lámpara", categoria="Hogar", precio=Decimal("25.75"))
    silla = Producto(nombre="Silla", categoria="Oficina", precio=Decimal("149.00"))
    session.add_all([lampara, silla])
    session.flush()
    session.add_all(
        [
            Venta(producto_id=lampara.id, cantidad=2, precio_unitario=Decimal("25.75"), fecha=date(2026, 1, 5)),
            Venta(producto_id=silla.id, cantidad=1, precio_unitario=Decimal("149.00"), fecha=date(2026, 1, 6)),
        ]
    )
    session.commit()

    resumen = calcular_resumen(session)

    # 2 * 25.75 + 1 * 149.00 = 200.50; ticket = 200.50 / 2 = 100.25
    assert resumen.ingresos_totales == Decimal("200.50")
    assert resumen.cantidad_vendida == 3
    assert resumen.numero_ventas == 2
    assert resumen.ticket_promedio == Decimal("100.25")
    assert [(c.categoria, c.cantidad_vendida, c.ingresos) for c in resumen.ventas_por_categoria] == [
        ("Hogar", 2, Decimal("51.50")),
        ("Oficina", 1, Decimal("149.00")),
    ]


def test_indicadores_coinciden_con_recalculo_sobre_datos_demo(session: Session):
    from app.seed import seed_demo_data

    seed_demo_data(session)
    esperado = _recalcular_en_python(session)

    resumen = calcular_resumen(session)

    assert resumen.ingresos_totales == esperado["ingresos_totales"]
    assert resumen.cantidad_vendida == esperado["cantidad_vendida"]
    assert resumen.numero_ventas == esperado["numero_ventas"] == 50
    assert resumen.ticket_promedio == esperado["ticket_promedio"]
    assert {
        c.categoria: {"cantidad_vendida": c.cantidad_vendida, "ingresos": c.ingresos}
        for c in resumen.ventas_por_categoria
    } == esperado["ventas_por_categoria"]


def test_endpoint_indicadores_responde_con_los_mismos_valores(client_con_datos: TestClient, session: Session):
    respuesta = client_con_datos.get("/api/indicadores")

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    esperado = _recalcular_en_python(session)
    assert cuerpo["ingresos_totales"] == float(esperado["ingresos_totales"])
    assert cuerpo["cantidad_vendida"] == esperado["cantidad_vendida"]
    assert cuerpo["numero_ventas"] == 50
    assert cuerpo["ticket_promedio"] == float(esperado["ticket_promedio"])
    assert sum(c["ingresos"] for c in cuerpo["ventas_por_categoria"]) == float(esperado["ingresos_totales"])
