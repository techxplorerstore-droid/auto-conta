"""Extracción de texto crudo desde facturas en PDF (pdfplumber).

Contrato: devuelve SOLO texto normalizado (str). No estructura ni parsea a
`Factura` — eso es responsabilidad de la capa de IA (lote LLM).
"""

from __future__ import annotations

import re
from pathlib import Path

import pdfplumber


def _normalizar(texto: str) -> str:
    """Colapsa espacios sobrantes y recorta líneas en blanco extra."""
    lineas = []
    for linea in texto.splitlines():
        linea = re.sub(r"[ \t]+", " ", linea).strip()
        lineas.append(linea)
    # Une las líneas y colapsa secuencias de >1 línea vacía en una sola.
    resultado = "\n".join(lineas)
    resultado = re.sub(r"\n{3,}", "\n\n", resultado)
    return resultado.strip()


def extraer_texto(path: Path) -> str:
    """Devuelve el texto plano de un PDF de factura.

    Itera todas las páginas, ignora las que no devuelven texto (None) y une el
    resultado con saltos de línea.

    Raises:
        FileNotFoundError: si el archivo no existe.
        ValueError: si no se pudo extraer texto del PDF.
    """
    if not path.exists():
        raise FileNotFoundError(f"El archivo PDF no existe: {path}")

    partes: list[str] = []
    with pdfplumber.open(path) as pdf:
        for pagina in pdf.pages:
            texto = pagina.extract_text()
            if texto:
                partes.append(texto)

    if not partes:
        raise ValueError(f"No se pudo extraer texto del PDF: {path}")

    texto_normalizado = _normalizar("\n".join(partes))
    if not texto_normalizado:
        raise ValueError(f"No se pudo extraer texto del PDF: {path}")

    return texto_normalizado
