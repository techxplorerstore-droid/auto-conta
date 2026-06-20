"""Modelos de datos (pydantic) para una factura estructurada.

Estos modelos definen el contrato de salida que la capa de IA debe respetar
y que se valida antes de consolidar el reporte. FASE 1: definición de esquema.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class CategoriaContable(str, Enum):
    """Set inicial de categorías contables para clasificar el gasto."""

    SERVICIOS_PUBLICOS = "servicios_publicos"
    PAPELERIA = "papeleria"
    ARRIENDO = "arriendo"
    TRANSPORTE = "transporte"
    TECNOLOGIA = "tecnologia"
    HONORARIOS = "honorarios"
    MANTENIMIENTO = "mantenimiento"
    ALIMENTACION = "alimentacion"
    MARKETING = "marketing"
    IMPUESTOS = "impuestos"
    OTROS = "otros"


class ItemFactura(BaseModel):
    """Una línea/ítem dentro de la factura."""

    descripcion: str = Field(..., description="Descripción del producto o servicio.")
    cantidad: Decimal = Field(default=Decimal("1"), description="Unidades facturadas.")
    valor_unitario: Optional[Decimal] = Field(
        default=None, description="Valor por unidad antes de impuestos."
    )
    valor_total: Optional[Decimal] = Field(
        default=None, description="Valor total de la línea."
    )


class Factura(BaseModel):
    """Representación estructurada y validada de una factura."""

    proveedor: str = Field(..., description="Razón social del proveedor.")
    nit: Optional[str] = Field(
        default=None, description="NIT / identificación tributaria del proveedor."
    )
    numero_factura: Optional[str] = Field(
        default=None, description="Número o consecutivo de la factura."
    )
    fecha: Optional[date] = Field(default=None, description="Fecha de emisión.")
    subtotal: Optional[Decimal] = Field(
        default=None, description="Valor antes de impuestos."
    )
    iva: Optional[Decimal] = Field(default=None, description="Valor del IVA.")
    total: Decimal = Field(..., description="Valor total a pagar.")
    categoria: CategoriaContable = Field(
        default=CategoriaContable.OTROS,
        description="Categoría contable asignada por la IA.",
    )
    items: List[ItemFactura] = Field(
        default_factory=list, description="Detalle de líneas de la factura."
    )
    archivo_origen: Optional[str] = Field(
        default=None, description="Nombre del archivo desde el que se extrajo."
    )
