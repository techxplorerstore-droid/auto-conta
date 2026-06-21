"""Tests de la generación del reporte consolidado (sin red)."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pandas as pd
import pytest

from auto_conta.models import CategoriaContable, Factura, ItemFactura
from auto_conta.report import generar_reporte


def _factura(numero, proveedor, categoria, subtotal, iva, total, origen):
    return Factura(
        numero_factura=numero,
        proveedor=proveedor,
        nit="900.000.000-0",
        fecha=date(2026, 2, 11),
        items=[
            ItemFactura(
                descripcion="item",
                cantidad=Decimal("1"),
                valor_unitario=Decimal(subtotal),
                valor_total=Decimal(subtotal),
            )
        ],
        subtotal=Decimal(subtotal),
        iva_valor=Decimal(iva),
        total=Decimal(total),
        categoria=categoria,
        archivo_origen=origen,
    )


@pytest.fixture
def facturas():
    return [
        _factura("F1", "Papelería X", CategoriaContable.PAPELERIA_OFICINA,
                 "643000", "122170", "765170", "f1.pdf"),
        _factura("F2", "Energía Y", CategoriaContable.SERVICIOS_PUBLICOS,
                 "660830", "125558", "786388", "f2.pdf"),
        _factura("F3", "Papelería Z", CategoriaContable.PAPELERIA_OFICINA,
                 "100000", "19000", "119000", "f3.xlsx"),
    ]


def test_genera_xlsx_con_detalle_y_resumen(facturas, tmp_path):
    salida = tmp_path / "reporte.xlsx"
    resultado = generar_reporte(facturas, salida)
    assert resultado == salida
    assert salida.exists()

    # Hoja "Facturas": 3 filas, totales correctos.
    detalle = pd.read_excel(salida, sheet_name="Facturas")
    assert len(detalle) == 3
    assert list(detalle["numero_factura"]) == ["F1", "F2", "F3"]
    assert detalle.loc[detalle["numero_factura"] == "F1", "total"].iloc[0] == 765170.0
    assert set(detalle["categoria"]) == {"papeleria_oficina", "servicios_publicos"}

    # Hoja "Resumen": suma por categoría + TOTAL general.
    resumen = pd.read_excel(salida, sheet_name="Resumen")
    fila_papeleria = resumen.loc[resumen["categoria"] == "papeleria_oficina"].iloc[0]
    assert fila_papeleria["cantidad_facturas"] == 2
    assert fila_papeleria["total"] == 765170.0 + 119000.0

    fila_servicios = resumen.loc[resumen["categoria"] == "servicios_publicos"].iloc[0]
    assert fila_servicios["cantidad_facturas"] == 1
    assert fila_servicios["total"] == 786388.0

    fila_total = resumen.loc[resumen["categoria"] == "TOTAL"].iloc[0]
    assert fila_total["cantidad_facturas"] == 3
    assert fila_total["total"] == 765170.0 + 786388.0 + 119000.0

    # Orden por total desc: papeleria (884170) > servicios (786388) antes del TOTAL.
    categorias_ordenadas = list(resumen["categoria"])
    assert categorias_ordenadas[0] == "papeleria_oficina"
    assert categorias_ordenadas[-1] == "TOTAL"


def test_genera_csv_solo_detalle(facturas, tmp_path):
    salida = tmp_path / "reporte.csv"
    resultado = generar_reporte(facturas, salida)
    assert resultado == salida
    assert salida.exists()

    detalle = pd.read_csv(salida)
    assert len(detalle) == 3
    assert list(detalle.columns)[:3] == ["numero_factura", "proveedor", "nit"]


def test_lista_vacia_lanza_valueerror(tmp_path):
    with pytest.raises(ValueError, match="No hay facturas"):
        generar_reporte([], tmp_path / "reporte.xlsx")


def test_extension_no_soportada_lanza_valueerror(facturas, tmp_path):
    with pytest.raises(ValueError, match="no soportada"):
        generar_reporte(facturas, tmp_path / "reporte.txt")
