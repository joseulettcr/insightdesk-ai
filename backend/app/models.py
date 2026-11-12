from datetime import date
from decimal import ROUND_HALF_UP, Decimal

from sqlalchemy import Date, ForeignKey, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.types import TypeDecorator


class Base(DeclarativeBase):
    pass


class Dinero(TypeDecorator):
    """Guarda importes como céntimos enteros para evitar errores de coma flotante."""

    impl = Integer
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return int((Decimal(value) * 100).to_integral_value(rounding=ROUND_HALF_UP))

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return (Decimal(value) / 100).quantize(Decimal("0.01"))


class Producto(Base):
    __tablename__ = "productos"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(120))
    categoria: Mapped[str] = mapped_column(String(60), index=True)
    precio: Mapped[Decimal] = mapped_column(Dinero)

    ventas: Mapped[list["Venta"]] = relationship(back_populates="producto")


class Venta(Base):
    __tablename__ = "ventas"

    id: Mapped[int] = mapped_column(primary_key=True)
    producto_id: Mapped[int] = mapped_column(ForeignKey("productos.id"), index=True)
    cantidad: Mapped[int]
    precio_unitario: Mapped[Decimal] = mapped_column(Dinero)
    fecha: Mapped[date] = mapped_column(Date, index=True)

    producto: Mapped[Producto] = relationship(back_populates="ventas")
