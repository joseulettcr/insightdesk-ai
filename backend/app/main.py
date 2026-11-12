from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.agente.gemini import crear_cliente_desde_entorno
from app.config import DATABASE_URL
from app.models import Base
from app.routers import agente, indicadores, productos, ventas


def _crear_engine(database_url: str):
    connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}
    return create_engine(database_url, connect_args=connect_args)


def create_app(database_url: str = DATABASE_URL, cliente_gemini=None) -> FastAPI:
    engine = _crear_engine(database_url)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        Base.metadata.create_all(engine)
        yield
        engine.dispose()

    app = FastAPI(title="InsightDesk AI", version="0.2.0", lifespan=lifespan)
    app.state.engine = engine
    app.state.session_factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    app.state.cliente_gemini = cliente_gemini

    app.include_router(productos.router)
    app.include_router(ventas.router)
    app.include_router(indicadores.router)
    app.include_router(agente.router)
    return app


app = create_app(cliente_gemini=crear_cliente_desde_entorno())
