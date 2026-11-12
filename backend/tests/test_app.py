from fastapi import FastAPI

from app.main import create_app


def test_create_app_returns_fastapi_instance():
    app = create_app()

    assert isinstance(app, FastAPI)
    assert app.title == "InsightDesk AI"


def test_openapi_schema_is_valid_json():
    schema = create_app().openapi()

    assert schema["info"]["title"] == "InsightDesk AI"
    assert schema["openapi"].startswith("3.")


def test_openapi_endpoint_responds_over_http():
    from fastapi.testclient import TestClient

    client = TestClient(create_app())
    response = client.get("/openapi.json")

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    assert response.json()["info"]["title"] == "InsightDesk AI"
