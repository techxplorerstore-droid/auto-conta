"""Extracción de datos crudos desde facturas en Excel.

FASE 1: solo stub. La implementación usará `pandas` (con `openpyxl` como motor)
para leer la hoja y serializar las filas a texto/registros para la capa de IA.
"""

from __future__ import annotations

from pathlib import Path


def extraer_texto_excel(ruta: Path) -> str:
    """Devuelve una representación textual del contenido de un Excel de factura.

    TODO(lote 2): leer con pandas.read_excel y serializar a texto/markdown.
    """
    raise NotImplementedError("extraer_texto_excel aún no implementado (FASE 1).")
