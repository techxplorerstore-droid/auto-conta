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
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


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

    model_config = ConfigDict(json_encoders={Decimal: str})

    descripcion: str = Field(..., description="Descripción del producto o servicio.")
    cantidad: Decimal = Field(..., description="Unidades facturadas.")
    valor_unitario: Decimal = Field(..., description="Valor por unidad antes de impuestos.")
    valor_total: Decimal = Field(..., description="Valor total de la línea (cantidad * unitario).")


class Factura(BaseModel):
    """Representación estructurada y validada de una factura."""

    model_config = ConfigDict(json_encoders={Decimal: str})

    numero_factura: str = Field(..., description="Número o consecutivo de la factura.")
    proveedor: str = Field(..., description="Razón social del proveedor.")
    nit: str = Field(..., description="NIT / identificación tributaria del proveedor.")
    fecha: date = Field(..., description="Fecha de emisión.")
    moneda: str = Field(default="COP", description="Código de moneda ISO (por defecto COP).")
    items: List[ItemFactura] = Field(
        default_factory=list, description="Detalle de líneas de la factura."
    )
    subtotal: Decimal = Field(..., description="Valor antes de impuestos.")
    iva_porcentaje: Decimal = Field(
        default=Decimal("19"), description="Porcentaje de IVA aplicado (típico 19 en Colombia)."
    )
    iva_valor: Decimal = Field(..., description="Valor del IVA en dinero.")
    total: Decimal = Field(..., description="Valor total a pagar (subtotal + IVA).")
    categoria: CategoriaContable = Field(
        default=CategoriaContable.OTROS,
        description="Categoría contable asignada por la IA.",
    )
    archivo_origen: Optional[str] = Field(
        default=None, description="Nombre del archivo desde el que se extrajo."
    )
