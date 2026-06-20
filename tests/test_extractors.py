"""Tests de los extractors contra las muestras sintéticas de samples/."""

from __future__ import annotations

from pathlib import Path

import pytest

from auto_conta.extractors import extraer
from auto_conta.extractors import excel_extractor, pdf_extractor

SAMPLES = Path(__file__).resolve().parent.parent / "samples"
PDF_PAPELERIA = SAMPLES / "factura_papeleria.pdf"
XLSX_HONORARIOS = SAMPLES / "factura_honorarios.xlsx"


def test_pdf_extractor_devuelve_texto_con_tokens_conocidos():
    texto = pdf_extractor.extraer_texto(PDF_PAPELERIA)
    assert texto.strip(), "el texto del PDF no debe estar vacío"
    assert "Papelería El Lápiz Dorado" in texto
    assert "765.170" in texto  # total a pagar


def test_excel_extractor_devuelve_texto_con_tokens_conocidos():
    texto = excel_extractor.extraer_texto(XLSX_HONORARIOS)
    assert texto.strip(), "el texto del Excel no debe estar vacío"
    assert "Consultores Asociados JM" in texto
    assert "3867500" in texto  # total
    assert "|" in texto  # serialización fila como "c1 | c2 | ..."


def test_router_despacha_pdf():
    assert pdf_extractor.extraer_texto(PDF_PAPELERIA) == extraer(PDF_PAPELERIA)


def test_router_despacha_excel():
    assert excel_extractor.extraer_texto(XLSX_HONORARIOS) == extraer(XLSX_HONORARIOS)


def test_router_extension_no_soportada(tmp_path):
    archivo = tmp_path / "nota.txt"
    archivo.write_text("contenido cualquiera")
    with pytest.raises(ValueError, match="no soportada"):
        extraer(archivo)


def test_pdf_inexistente_lanza_error():
    with pytest.raises(FileNotFoundError):
        pdf_extractor.extraer_texto(SAMPLES / "no_existe.pdf")


def test_excel_inexistente_lanza_error():
    with pytest.raises(FileNotFoundError):
        excel_extractor.extraer_texto(SAMPLES / "no_existe.xlsx")
