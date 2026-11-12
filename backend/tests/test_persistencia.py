from fastapi.testclient import TestClient


from app.main import create_app
from app.models import Base
from app.seed import seed_demo_data


def test_ventas_persisten_tras_reiniciar_la_aplicacion(database_url: str):
    primera = create_app(database_url)
    Base.metadata.create_all(primera.state.engine)
    with primera.state.session_factory() as session:
        seed_demo_data(session)
    with TestClient(primera) as client:
        registrada = client.post(
            "/api/ventas", json={"producto_id": 3, "cantidad": 4, "precio_unitario": 170}
        ).json()
    primera.state.engine.dispose()

    segunda = create_app(database_url)
    with TestClient(segunda) as client:
        ventas = client.get("/api/ventas").json()
        indicadores = client.get("/api/indicadores").json()
    segunda.state.engine.dispose()

    assert len(ventas) == 51
    assert registrada["id"] in {v["id"] for v in ventas}
    assert indicadores["numero_ventas"] == 51
