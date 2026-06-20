"""Generación del reporte contable consolidado.

FASE 1: solo stub. La implementación tomará una lista de `Factura` validadas,
las volcará a un DataFrame de pandas y exportará a Excel (openpyxl) o CSV.
"""

from __future__ import annotations

from pathlib import Path
from typing import List

from auto_conta.models import Factura


def generar_reporte(facturas: List[Factura], salida: Path) -> Path:
    """Consolida las facturas en un único archivo Excel/CSV.

    TODO(lote 4): aplanar facturas a filas, crear DataFrame y exportar según
    la extensión de `salida` (.xlsx -> openpyxl, .csv -> to_csv).
    """
    raise NotImplementedError("generar_reporte aún no implementado (FASE 1).")
