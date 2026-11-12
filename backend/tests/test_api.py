from datetime import date, timedelta

from fastapi.testclient import TestClient


def test_listar_productos_devuelve_catalogo_demo(client_con_datos: TestClient):
    respuesta = client_con_datos.get("/api/productos")

    assert respuesta.status_code == 200
    productos = respuesta.json()
    assert len(productos) == 10
    assert productos[0]["precio"] == 59.9
    assert set(productos[0]) == {"id", "nombre", "categoria", "precio"}


def test_crear_producto_valido(client: TestClient):
    respuesta = client.post(
        "/api/productos",
        json={"nombre": "  Mesa plegable  ", "categoria": "Oficina", "precio": 79.5},
    )

    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo["nombre"] == "Mesa plegable"
    assert cuerpo["precio"] == 79.5
    assert isinstance(cuerpo["id"], int)


def test_crear_producto_rechaza_datos_invalidos(client: TestClient):
    casos = [
        {"nombre": "", "categoria": "Oficina", "precio": 10},
        {"nombre": "   ", "categoria": "Oficina", "precio": 10},
        {"nombre": "Mesa", "categoria": "Oficina", "precio": 0},
        {"nombre": "Mesa", "categoria": "Oficina", "precio": -5},
        {"nombre": "Mesa", "categoria": "Oficina", "precio": 1.999},
        {"nombre": "Mesa", "precio": 10},
    ]
    for cuerpo in casos:
        assert client.post("/api/productos", json=cuerpo).status_code == 422, cuerpo


def test_registrar_venta_usa_precio_del_producto_por_defecto(client_con_datos: TestClient):
    respuesta = client_con_datos.post("/api/ventas", json={"producto_id": 1, "cantidad": 3})

    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo["precio_unitario"] == 59.9
    assert cuerpo["cantidad"] == 3
    assert cuerpo["fecha"] == date.today().isoformat()


def test_registrar_venta_con_precio_y_fecha_explicitos(client_con_datos: TestClient):
    fecha = (date.today() - timedelta(days=2)).isoformat()

    respuesta = client_con_datos.post(
        "/api/ventas",
        json={"producto_id": 2, "cantidad": 1, "precio_unitario": 85, "fecha": fecha},
    )

    assert respuesta.status_code == 201
    assert respuesta.json()["precio_unitario"] == 85
    assert respuesta.json()["fecha"] == fecha


def test_registrar_venta_rechaza_datos_invalidos(client_con_datos: TestClient):
    manana = (date.today() + timedelta(days=1)).isoformat()
    casos = [
        {"producto_id": 1, "cantidad": 0},
        {"producto_id": 1, "cantidad": -1},
        {"producto_id": 0, "cantidad": 1},
        {"producto_id": 1, "cantidad": 1, "precio_unitario": 0},
        {"producto_id": 1, "cantidad": 1, "fecha": manana},
        {"producto_id": 1, "cantidad": 1, "fecha": "no-es-fecha"},
    ]
    for cuerpo in casos:
        assert client_con_datos.post("/api/ventas", json=cuerpo).status_code == 422, cuerpo


def test_registrar_venta_de_producto_inexistente_devuelve_404(client_con_datos: TestClient):
    respuesta = client_con_datos.post("/api/ventas", json={"producto_id": 999, "cantidad": 1})

    assert respuesta.status_code == 404
    assert respuesta.json() == {"detail": "Producto no encontrado"}


def test_listar_ventas_refleja_las_nuevas(client_con_datos: TestClient):
    client_con_datos.post("/api/ventas", json={"producto_id": 1, "cantidad": 2})

    ventas = client_con_datos.get("/api/ventas").json()

    assert len(ventas) == 51
    assert set(ventas[0]) == {"id", "producto_id", "cantidad", "precio_unitario", "fecha"}


def test_venta_nueva_actualiza_indicadores(client_con_datos: TestClient):
    antes = client_con_datos.get("/api/indicadores").json()

    client_con_datos.post("/api/ventas", json={"producto_id": 1, "cantidad": 2, "precio_unitario": 10})
    despues = client_con_datos.get("/api/indicadores").json()

    assert despues["numero_ventas"] == antes["numero_ventas"] + 1
    assert despues["cantidad_vendida"] == antes["cantidad_vendida"] + 2
    assert round(despues["ingresos_totales"] - antes["ingresos_totales"], 2) == 20.0
