"""Generación del reporte contable consolidado (Excel/CSV) con pandas.

Toma una lista de `Factura` validadas y produce una vista consolidada. Los
montos exactos viven en los objetos `Factura` (Decimal); el reporte es solo
una vista, por lo que los montos se convierten a float para las columnas
numéricas.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from typing import List

import pandas as pd

from auto_conta.models import Factura

COLUMNAS_DETALLE = [
    "numero_factura",
    "proveedor",
    "nit",
    "fecha",
    "categoria",
    "subtotal",
    "iva_valor",
    "total",
    "archivo_origen",
]


def _f(valor: Decimal) -> float:
    """Convierte un Decimal a float para las columnas numéricas del reporte."""
    return float(valor)


def _df_detalle(facturas: List[Factura]) -> pd.DataFrame:
    filas = [
        {
            "numero_factura": f.numero_factura,
            "proveedor": f.proveedor,
            "nit": f.nit,
            "fecha": f.fecha.isoformat(),
            "categoria": f.categoria.value,
            "subtotal": _f(f.subtotal),
            "iva_valor": _f(f.iva_valor),
            "total": _f(f.total),
            "archivo_origen": f.archivo_origen,
        }
        for f in facturas
    ]
    return pd.DataFrame(filas, columns=COLUMNAS_DETALLE)


def _df_resumen(detalle: pd.DataFrame) -> pd.DataFrame:
    """Agrupa por categoría (cantidad + suma de total), ordena desc y agrega TOTAL."""
    resumen = (
        detalle.groupby("categoria")
        .agg(cantidad_facturas=("numero_factura", "count"), total=("total", "sum"))
        .reset_index()
        .sort_values("total", ascending=False)
        .reset_index(drop=True)
    )
    fila_total = pd.DataFrame(
        [
            {
                "categoria": "TOTAL",
                "cantidad_facturas": int(resumen["cantidad_facturas"].sum()),
                "total": float(resumen["total"].sum()),
            }
        ]
    )
    return pd.concat([resumen, fila_total], ignore_index=True)


def generar_reporte(facturas: List[Factura], ruta_salida: Path) -> Path:
    """Consolida las facturas en un único archivo Excel/CSV.

    Args:
        facturas: lista de `Factura` validadas.
        ruta_salida: destino; .xlsx (dos hojas) o .csv (solo detalle).

    Returns:
        La ruta de salida.

    Raises:
        ValueError: si la lista está vacía o la extensión no está soportada.
    """
    if not facturas:
        raise ValueError("No hay facturas para generar el reporte.")

    detalle = _df_detalle(facturas)
    ext = ruta_salida.suffix.lower()

    if ext == ".xlsx":
        resumen = _df_resumen(detalle)
        with pd.ExcelWriter(ruta_salida, engine="openpyxl") as writer:
            detalle.to_excel(writer, sheet_name="Facturas", index=False)
            resumen.to_excel(writer, sheet_name="Resumen", index=False)
    elif ext == ".csv":
        detalle.to_csv(ruta_salida, index=False)
    else:
        raise ValueError(
            f"Extensión de salida no soportada: '{ext}'. Use .xlsx o .csv."
        )

    return ruta_salida
