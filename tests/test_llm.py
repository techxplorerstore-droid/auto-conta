"""Tests de la capa LLM.

- Unitario con el cliente Gemini MOCKEADO (sin red ni API key).
- Error claro de la factory cuando falta GEMINI_API_KEY.
- Integración OPCIONAL: se salta si no hay GEMINI_API_KEY.
"""

from __future__ import annotations

import os
from decimal import Decimal
from pathlib import Path
from unittest import mock

import pytest

from auto_conta.models import CategoriaContable, Factura

SAMPLES = Path(__file__).resolve().parent.parent / "samples"

# Respuesta JSON simulada: mezcla números y strings para ejercitar la
# coerción a Decimal sin pérdida de precisión (subtotal con centavos).
JSON_RESPUESTA = """{
  "numero_factura": "FE-2026-00187",
  "proveedor": "Papelería El Lápiz Dorado S.A.S.",
  "nit": "900.451.882-3",
  "fecha": "2026-02-11",
  "moneda": "COP",
  "items": [
    {"descripcion": "Resma papel carta 75g", "cantidad": 10, "valor_unitario": "18500.50", "valor_total": 185005}
  ],
  "subtotal": "643000.50",
  "iva_porcentaje": 19,
  "iva_valor": 122170,
  "total": 765170,
  "categoria": "papeleria_oficina"
}"""


@mock.patch("auto_conta.llm.gemini.genai.Client")
def test_estructurar_factura_con_cliente_mockeado(mock_client_cls):
    mock_client = mock_client_cls.return_value
    mock_response = mock.Mock()
    mock_response.text = JSON_RESPUESTA
    mock_client.models.generate_content.return_value = mock_response

    from auto_conta.llm.gemini import GeminiProvider

    provider = GeminiProvider(api_key="fake-key", modelo="gemini-2.5-flash")
    factura = provider.estructurar_factura(
        "texto crudo de la factura", archivo_origen="factura_papeleria.pdf"
    )

    assert isinstance(factura, Factura)
    assert factura.proveedor == "Papelería El Lápiz Dorado S.A.S."
    assert factura.categoria == CategoriaContable.PAPELERIA_OFICINA
    assert factura.archivo_origen == "factura_papeleria.pdf"

    # Montos como Decimal, con precisión exacta (números y strings).
    assert isinstance(factura.total, Decimal)
    assert factura.total == Decimal("765170")
    assert factura.subtotal == Decimal("643000.50")
    assert factura.items[0].valor_unitario == Decimal("18500.50")

    mock_client.models.generate_content.assert_called_once()


def test_crear_proveedor_sin_api_key(monkeypatch):
    # Aislar de entorno y de un eventual .env real.
    monkeypatch.setattr("auto_conta.llm.base.load_dotenv", lambda *a, **k: None)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    from auto_conta.llm.base import crear_proveedor

    with pytest.raises(ValueError, match="GEMINI_API_KEY"):
        crear_proveedor()


def test_crear_proveedor_no_soportado(monkeypatch):
    monkeypatch.setattr("auto_conta.llm.base.load_dotenv", lambda *a, **k: None)
    monkeypatch.setenv("GEMINI_API_KEY", "fake-key")

    from auto_conta.llm.base import crear_proveedor

    with pytest.raises(ValueError, match="no soportado"):
        crear_proveedor("claude")


@pytest.mark.skipif(
    not os.environ.get("GEMINI_API_KEY"),
    reason="requiere GEMINI_API_KEY (test de integración real contra Gemini)",
)
def test_integracion_gemini_sobre_pdf_real():
    from auto_conta.extractors import extraer
    from auto_conta.llm.base import crear_proveedor

    texto = extraer(SAMPLES / "factura_papeleria.pdf")
    provider = crear_proveedor()
    factura = provider.estructurar_factura(texto, archivo_origen="factura_papeleria.pdf")

    assert isinstance(factura, Factura)
    assert factura.proveedor
    assert factura.total > 0
    assert factura.categoria in CategoriaContable
