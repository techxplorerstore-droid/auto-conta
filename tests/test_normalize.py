"""Tests de la normalización de NIT y el dígito de verificación (DV)."""

from __future__ import annotations

import pytest

from auto_conta.normalize import calcular_dv, normalizar_nit, validar_nit


def test_calcular_dv_vector_dian():
    # Vector conocido DIAN.
    assert calcular_dv("800197268") == 4


@pytest.mark.parametrize("base", ["900451882", "860998331", "830.112.998"])
def test_calcular_dv_round_trip(base):
    dv = calcular_dv(base)
    digitos = base.replace(".", "")
    # El DV calculado valida; alterarlo invalida.
    assert validar_nit(f"{digitos}-{dv}") is True
    assert validar_nit(f"{digitos}-{(dv + 1) % 10}") is False


def test_calcular_dv_ignora_no_digitos():
    assert calcular_dv("800.197.268") == calcular_dv("800197268")


def test_calcular_dv_malformado_lanza():
    with pytest.raises(ValueError):
        calcular_dv("sin-digitos")
    with pytest.raises(ValueError):
        calcular_dv("1234567890123456")  # 16 dígitos > 15


@pytest.mark.parametrize(
    "crudo,esperado",
    [
        ("900.451.882-3", "900451882-3"),
        ("900451882-3", "900451882-3"),
        ("900 451 882 - 3", "900451882-3"),
        ("860.998.331", "860998331"),  # sin DV declarado: no se inventa
    ],
)
def test_normalizar_nit(crudo, esperado):
    assert normalizar_nit(crudo) == esperado


def test_validar_nit():
    assert validar_nit("800197268-4") is True
    assert validar_nit("800197268-5") is False  # DV alterado
    assert validar_nit("800197268") is False     # sin DV declarado
    assert validar_nit("no-es-nit") is False      # malformado
    assert validar_nit("") is False
