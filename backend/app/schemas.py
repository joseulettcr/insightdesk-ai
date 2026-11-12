from datetime import date
from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, PlainSerializer, field_validator

Importe = Annotated[
    Decimal,
    PlainSerializer(float, return_type=float, when_used="json"),
]


def _limpiar_texto(valor: str) -> str:
    texto = valor.strip()
    if not texto:
        raise ValueError("no puede estar vacío")
    return texto


class ProductoCreate(BaseModel):
    nombre: str = Field(min_length=1, max_length=120)
    categoria: str = Field(min_length=1, max_length=60)
    precio: Decimal = Field(gt=0, max_digits=12, decimal_places=2)

    _limpiar_nombre = field_validator("nombre", "categoria")(_limpiar_texto)


class ProductoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    categoria: str
    precio: Importe


class VentaCreate(BaseModel):
    producto_id: int = Field(gt=0)
    cantidad: int = Field(ge=1, le=10_000)
    precio_unitario: Decimal | None = Field(default=None, gt=0, max_digits=12, decimal_places=2)
    fecha: date | None = None

    @field_validator("fecha")
    @classmethod
    def no_futura(cls, valor: date | None) -> date | None:
        if valor is not None and valor > date.today():
            raise ValueError("no puede ser una fecha futura")
        return valor


class VentaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    producto_id: int
    cantidad: int
    precio_unitario: Importe
    fecha: date


class CategoriaIndicador(BaseModel):
    categoria: str
    cantidad_vendida: int
    ingresos: Importe


class IndicadoresOut(BaseModel):
    ingresos_totales: Importe
    cantidad_vendida: int
    numero_ventas: int
    ticket_promedio: Importe
    ventas_por_categoria: list[CategoriaIndicador]


class ChatRequest(BaseModel):
    mensaje: str = Field(min_length=1, max_length=1000)

    _limpiar_mensaje = field_validator("mensaje")(_limpiar_texto)


class ChatResponse(BaseModel):
    respuesta: str
    herramientas_usadas: list[str]
