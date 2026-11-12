from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.indicadores import calcular_resumen
from app.schemas import IndicadoresOut
from app.session import get_session

router = APIRouter(prefix="/api/indicadores", tags=["indicadores"])


@router.get("", response_model=IndicadoresOut)
def obtener_indicadores(session: Session = Depends(get_session)):
    resumen = calcular_resumen(session)
    return {
        "ingresos_totales": resumen.ingresos_totales,
        "cantidad_vendida": resumen.cantidad_vendida,
        "numero_ventas": resumen.numero_ventas,
        "ticket_promedio": resumen.ticket_promedio,
        "ventas_por_categoria": [
            {
                "categoria": c.categoria,
                "cantidad_vendida": c.cantidad_vendida,
                "ingresos": c.ingresos,
            }
            for c in resumen.ventas_por_categoria
        ],
    }
