from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Producto
from app.schemas import ProductoCreate, ProductoOut
from app.session import get_session

router = APIRouter(prefix="/api/productos", tags=["productos"])


@router.get("", response_model=list[ProductoOut])
def listar_productos(session: Session = Depends(get_session)):
    return session.scalars(select(Producto).order_by(Producto.id)).all()


@router.post("", response_model=ProductoOut, status_code=status.HTTP_201_CREATED)
def crear_producto(datos: ProductoCreate, session: Session = Depends(get_session)):
    producto = Producto(nombre=datos.nombre, categoria=datos.categoria, precio=datos.precio)
    session.add(producto)
    session.commit()
    session.refresh(producto)
    return producto
