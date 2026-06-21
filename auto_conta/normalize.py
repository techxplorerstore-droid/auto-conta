"""Normalización determinística de NIT colombiano + dígito de verificación (DV).

Funciones puras, sin dependencias del resto del paquete. La normalización solo
REFORMATEA lo que hay; nunca inventa datos (si no viene DV, no se fabrica).
"""

from __future__ import annotations

import re

# Pesos DIAN (módulo 11), aplicados de DERECHA a IZQUIERDA. Soporta hasta 15
# dígitos de base.
PESOS_DV = [3, 7, 13, 17, 19, 23, 29, 37, 41, 43, 47, 53, 59, 67, 71]


def _solo_digitos(texto: str) -> str:
    return re.sub(r"\D", "", texto or "")


def calcular_dv(base: str) -> int:
    """Calcula el dígito de verificación DIAN (módulo 11) de la base de un NIT.

    Args:
        base: número base del NIT (se ignoran puntos/espacios/no-dígitos).

    Returns:
        El DV (0-9).

    Raises:
        ValueError: si la base no tiene dígitos o excede 15 dígitos.
    """
    digitos = _solo_digitos(base)
    if not digitos:
        raise ValueError("La base del NIT no contiene dígitos.")
    if len(digitos) > len(PESOS_DV):
        raise ValueError(
            f"La base del NIT excede {len(PESOS_DV)} dígitos: {len(digitos)}."
        )

    suma = sum(int(d) * PESOS_DV[i] for i, d in enumerate(reversed(digitos)))
    residuo = suma % 11
    return residuo if residuo in (0, 1) else 11 - residuo


def normalizar_nit(crudo: str) -> str:
    """Lleva un NIT a su forma canónica: "<base_digitos>-<DV>" (sin puntos).

    - Si viene un guion, lo que sigue es el DV declarado y se conserva.
    - Si NO viene DV declarado, se devuelve solo la base (no se inventa el DV).

    Solo reformatea; no valida el DV.
    """
    if crudo is None:
        return crudo

    s = str(crudo).strip()
    if "-" in s:
        base_part, dv_part = s.rsplit("-", 1)
        base = _solo_digitos(base_part)
        dv = _solo_digitos(dv_part)
        if base and dv:
            return f"{base}-{dv}"
        return base or s

    base = _solo_digitos(s)
    return base or s


def validar_nit(crudo: str) -> bool:
    """True si el DV declarado coincide con el DV calculado de la base.

    False si no hay DV declarado, está malformado, o el DV no coincide.
    """
    if not crudo or "-" not in str(crudo):
        return False

    base_part, dv_part = str(crudo).rsplit("-", 1)
    base = _solo_digitos(base_part)
    dv = _solo_digitos(dv_part)
    if not base or not dv:
        return False

    try:
        return calcular_dv(base) == int(dv)
    except ValueError:
        return False
