"""Extracción de texto crudo desde facturas en PDF.

FASE 1: solo stub. La implementación usará `pdfplumber` para abrir el PDF
y concatenar el texto de cada página, que luego se le pasa a la capa de IA.
"""

from __future__ import annotations

from pathlib import Path


def extraer_texto_pdf(ruta: Path) -> str:
    """Devuelve el texto plano de un PDF de factura.

    TODO(lote 2): abrir con pdfplumber, iterar páginas y unir page.extract_text().
    """
    raise NotImplementedError("extraer_texto_pdf aún no implementado (FASE 1).")
