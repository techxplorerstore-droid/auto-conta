"""Extractores de texto crudo desde archivos de facturas (PDF, Excel).

Punto de entrada: `extraer(path)`, que despacha al extractor correcto según la
extensión. Todos los extractors devuelven SOLO texto normalizado (str).
"""

from __future__ import annotations

from pathlib import Path

from auto_conta.extractors import excel_extractor, pdf_extractor

EXTENSIONES_SOPORTADAS = (".pdf", ".xlsx", ".xls")


def extraer(path: Path) -> str:
    """Extrae el texto de una factura despachando por extensión.

    Args:
        path: ruta al archivo (.pdf, .xlsx o .xls).

    Returns:
        Texto normalizado del documento.

    Raises:
        ValueError: si la extensión no está soportada.
    """
    ext = path.suffix.lower()
    if ext == ".pdf":
        return pdf_extractor.extraer_texto(path)
    if ext in (".xlsx", ".xls"):
        return excel_extractor.extraer_texto(path)
    raise ValueError(
        f"Extensión no soportada: '{ext}'. "
        f"Soportadas: {', '.join(EXTENSIONES_SOPORTADAS)}."
    )
