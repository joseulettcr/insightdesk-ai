from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Producto, Venta
from app.schemas import VentaCreate, VentaOut
from app.session import get_session

router = APIRouter(prefix="/api/ventas", tags=["ventas"])


@router.get("", response_model=list[VentaOut])
def listar_ventas(session: Session = Depends(get_session)):
    return session.scalars(select(Venta).order_by(Venta.fecha, Venta.id)).all()


@router.post("", response_model=VentaOut, status_code=status.HTTP_201_CREATED)
def registrar_venta(datos: VentaCreate, session: Session = Depends(get_session)):
    producto = session.get(Producto, datos.producto_id)
    if producto is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")

    venta = Venta(
        producto_id=producto.id,
        cantidad=datos.cantidad,
        precio_unitario=datos.precio_unitario or producto.precio,
        fecha=datos.fecha or date.today(),
    )
    session.add(venta)
    session.commit()
    session.refresh(venta)
    return venta
