from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.agente.errores import AgenteError
from app.agente.herramientas import construir_herramientas
from app.agente.registro import registrar
from app.agente.servicio import responder
from app.config import GEMINI_MODEL
from app.schemas import ChatRequest, ChatResponse
from app.session import get_session

router = APIRouter(prefix="/api/agente", tags=["agente"])


@router.post("/chat", response_model=ChatResponse)
def chat(datos: ChatRequest, request: Request, session: Session = Depends(get_session)):
    cliente = request.app.state.cliente_gemini
    if cliente is None:
        registrar(503, "No configurado", "Falta GEMINI_API_KEY en el servidor.")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="El asistente no está configurado en el servidor.",
        )

    herramientas = construir_herramientas(session)
    try:
        resultado = responder(cliente, herramientas, datos.mensaje, GEMINI_MODEL)
    except AgenteError as error:
        raise HTTPException(status_code=error.status_code, detail=error.detail) from None

    return ChatResponse(respuesta=resultado.texto, herramientas_usadas=resultado.herramientas_usadas)
