"""Punto de entrada de la CLI de auto-conta.

FASE 1: solo el esqueleto del comando. Sin lógica real todavía.
La orquestación (extraer -> estructurar con IA -> validar -> reportar)
se implementará en lotes posteriores.
"""

from __future__ import annotations

import argparse
from pathlib import Path


def build_parser() -> argparse.ArgumentParser:
    """Define la interfaz de línea de comandos.

    El diseño previsto es:
        auto-conta procesar <carpeta_facturas> --salida reporte.xlsx
    """
    parser = argparse.ArgumentParser(
        prog="auto-conta",
        description="Extrae y categoriza datos contables de facturas (PDF/Excel) usando IA.",
    )
    sub = parser.add_subparsers(dest="comando")

    procesar = sub.add_parser(
        "procesar",
        help="Procesa una carpeta de facturas y genera un reporte consolidado.",
    )
    procesar.add_argument(
        "carpeta",
        type=Path,
        help="Carpeta que contiene las facturas en PDF y/o Excel.",
    )
    procesar.add_argument(
        "-s",
        "--salida",
        type=Path,
        default=Path("reporte.xlsx"),
        help="Ruta del reporte consolidado de salida (por defecto: reporte.xlsx).",
    )
    procesar.add_argument(
        "--proveedor-llm",
        default="gemini",
        choices=["gemini", "claude"],
        help="Proveedor de IA a utilizar (por defecto: gemini).",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    """Esqueleto del flujo principal. TODO(lote): conectar el pipeline real."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.comando is None:
        parser.print_help()
        return 0

    # TODO(lote 5): orquestar extractors -> llm -> models -> report.
    raise NotImplementedError(
        "El comando 'procesar' aún no está implementado (FASE 1: scaffolding)."
    )


if __name__ == "__main__":
    raise SystemExit(main())
