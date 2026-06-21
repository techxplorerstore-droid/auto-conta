"""Tests del CLI end-to-end con proveedor de IA FALSO (sin red ni API key).

La extracción de texto corre de verdad sobre samples/; solo se reemplaza la
capa LLM por un fake que devuelve Facturas prefabricadas.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from pathlib import Path

import pandas as pd
import pytest

from auto_conta import cli
from auto_conta.models import CategoriaContable, Factura, ItemFactura

SAMPLES = Path(__file__).resolve().parent.parent / "samples"
N_SAMPLES = 7  # 5 PDF + 2 XLSX


def _factura_fake(origen: str | None) -> Factura:
    return Factura(
        numero_factura=f"F-{origen}",
        proveedor=f"Proveedor {origen}",
        nit="900.000.000-0",
        fecha=date(2026, 2, 11),
        items=[
            ItemFactura(
                descripcion="item",
                cantidad=Decimal("1"),
                valor_unitario=Decimal("1000"),
                valor_total=Decimal("1000"),
            )
        ],
        subtotal=Decimal("1000"),
        iva_valor=Decimal("190"),
        total=Decimal("1190"),
        categoria=CategoriaContable.OTROS,
        archivo_origen=origen,
    )


class _FakeProvider:
    def estructurar_factura(self, texto: str, archivo_origen: str | None = None) -> Factura:
        return _factura_fake(archivo_origen)


class _FakeProviderConFallo:
    def __init__(self, archivo_que_falla: str) -> None:
        self.archivo_que_falla = archivo_que_falla

    def estructurar_factura(self, texto: str, archivo_origen: str | None = None) -> Factura:
        if archivo_origen == self.archivo_que_falla:
            raise RuntimeError("fallo simulado de estructuración")
        return _factura_fake(archivo_origen)


def test_cli_procesa_samples_y_genera_reporte(monkeypatch, tmp_path):
    monkeypatch.setattr(cli, "crear_proveedor", lambda nombre="gemini": _FakeProvider())
    salida = tmp_path / "reporte.xlsx"

    ret = cli.main([str(SAMPLES), "-o", str(salida)])

    assert ret == 0
    assert salida.exists()
    detalle = pd.read_excel(salida, sheet_name="Facturas")
    assert len(detalle) == N_SAMPLES


def test_cli_continua_ante_fallo_de_un_archivo(monkeypatch, tmp_path, capsys):
    fake = _FakeProviderConFallo("factura_energia.pdf")
    monkeypatch.setattr(cli, "crear_proveedor", lambda nombre="gemini": fake)
    salida = tmp_path / "reporte.xlsx"

    ret = cli.main([str(SAMPLES), "-o", str(salida)])

    # El lote sigue: las demás se procesan (exit 0) y el reporte tiene N-1 filas.
    assert ret == 0
    detalle = pd.read_excel(salida, sheet_name="Facturas")
    assert len(detalle) == N_SAMPLES - 1
    assert "factura_energia.pdf" not in set(detalle["archivo_origen"])

    salida_txt = capsys.readouterr().out
    assert "factura_energia.pdf" in salida_txt  # el fallo se reporta
    assert "1" in salida_txt  # cuenta de fallidas


def test_cli_carpeta_sin_archivos_soportados(monkeypatch, tmp_path):
    monkeypatch.setattr(cli, "crear_proveedor", lambda nombre="gemini": _FakeProvider())
    vacia = tmp_path / "vacia"
    vacia.mkdir()
    (vacia / "nota.txt").write_text("no es factura")

    ret = cli.main([str(vacia), "-o", str(tmp_path / "reporte.xlsx")])

    assert ret != 0
    assert not (tmp_path / "reporte.xlsx").exists()
