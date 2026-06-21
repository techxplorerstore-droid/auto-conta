"""Modelos de datos (pydantic) para una factura estructurada.

Estos modelos definen el contrato de salida que la capa de IA debe respetar
y que se valida antes de consolidar el reporte.

Decisiones de diseño:
- Todos los montos son `Decimal` (NUNCA float): evita errores de redondeo en
  cálculos contables. La config de pydantic los serializa como string para no
  perder precisión al exportar a JSON.
- `fecha` es `datetime.date`.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from enum import Enum
from typing import Annotated, List, Optional

from pydantic import BaseModel, Field, PlainSerializer

# Tipo de monto reutilizable: Decimal en Python, serializado como string SOLO
# en JSON (when_used="json"), preservando precisión sin perder el tipo Decimal
# en model_dump(). Reemplaza al deprecado ConfigDict(json_encoders=...).
MontoDecimal = Annotated[
    Decimal,
    PlainSerializer(lambda v: str(v), return_type=str, when_used="json"),
]


class CategoriaContable(str, Enum):
    """Set de categorías contables para clasificar el gasto (contexto Colombia)."""

    SERVICIOS_PUBLICOS = "servicios_publicos"
    PAPELERIA_OFICINA = "papeleria_oficina"
    ARRIENDO = "arriendo"
    TRANSPORTE = "transporte"
    TECNOLOGIA = "tecnologia"
    MANTENIMIENTO = "mantenimiento"
    HONORARIOS = "honorarios"
    OTROS = "otros"


class ItemFactura(BaseModel):
    """Una línea/ítem dentro de la factura."""

    descripcion: str = Field(..., description="Descripción del producto o servicio.")
    cantidad: MontoDecimal = Field(..., description="Unidades facturadas.")
    valor_unitario: MontoDecimal = Field(..., description="Valor por unidad antes de impuestos.")
    valor_total: MontoDecimal = Field(..., description="Valor total de la línea (cantidad * unitario).")


class Factura(BaseModel):
    """Representación estructurada y validada de una factura."""

    numero_factura: str = Field(..., description="Número o consecutivo de la factura.")
    proveedor: str = Field(..., description="Razón social del proveedor.")
    nit: str = Field(..., description="NIT / identificación tributaria del proveedor.")
    fecha: date = Field(..., description="Fecha de emisión.")
    moneda: str = Field(default="COP", description="Código de moneda ISO (por defecto COP).")
    items: List[ItemFactura] = Field(
        default_factory=list, description="Detalle de líneas de la factura."
    )
    subtotal: MontoDecimal = Field(..., description="Valor antes de impuestos.")
    iva_porcentaje: MontoDecimal = Field(
        default=Decimal("19"), description="Porcentaje de IVA aplicado (típico 19 en Colombia)."
    )
    iva_valor: MontoDecimal = Field(..., description="Valor del IVA en dinero.")
    total: MontoDecimal = Field(..., description="Valor total a pagar (subtotal + IVA).")
    categoria: CategoriaContable = Field(
        default=CategoriaContable.OTROS,
        description="Categoría contable asignada por la IA.",
    )
    archivo_origen: Optional[str] = Field(
        default=None, description="Nombre del archivo desde el que se extrajo."
    )
