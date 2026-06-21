"""Punto de entrada de la CLI de auto-conta.

Orquesta el pipeline completo:
    carpeta de facturas -> extraer texto -> estructurar con IA -> reporte.

Uso:
    python -m auto_conta <carpeta> [-o reporte.xlsx] [--provider gemini]
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import List, Optional, Tuple

from rich.console import Console
from rich.table import Table

from auto_conta.extractors import EXTENSIONES_SOPORTADAS, extraer
from auto_conta.llm.base import crear_proveedor
from auto_conta.models import Factura
from auto_conta.normalize import validar_nit
from auto_conta.report import generar_reporte

console = Console()


def build_parser() -> argparse.ArgumentParser:
    """Define la interfaz de línea de comandos."""
    parser = argparse.ArgumentParser(
        prog="auto-conta",
        description="Extrae y categoriza datos contables de facturas (PDF/Excel) usando IA.",
    )
    parser.add_argument(
        "carpeta",
        type=Path,
        help="Carpeta que contiene las facturas en PDF y/o Excel.",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("reporte.xlsx"),
        help="Ruta del reporte consolidado (.xlsx o .csv). Por defecto: reporte.xlsx.",
    )
    parser.add_argument(
        "--provider",
        default="gemini",
        help="Proveedor de IA a utilizar (por defecto: gemini).",
    )
    return parser


def _buscar_archivos(carpeta: Path) -> List[Path]:
    """Devuelve los archivos soportados de la carpeta, ordenados."""
    return sorted(
        p
        for p in carpeta.iterdir()
        if p.is_file() and p.suffix.lower() in EXTENSIONES_SOPORTADAS
    )


def _imprimir_resumen(
    procesadas: int,
    fallidos: List[Tuple[str, str]],
    nits_inconsistentes: List[str],
    reporte: Optional[Path],
) -> None:
    tabla = Table(title="Resumen", show_header=True, header_style="bold")
    tabla.add_column("Métrica")
    tabla.add_column("Valor", justify="right")
    tabla.add_row("Facturas procesadas", str(procesadas))
    tabla.add_row("Facturas fallidas", str(len(fallidos)))
    tabla.add_row("Total de archivos", str(procesadas + len(fallidos)))
    tabla.add_row("NITs con DV inconsistente", str(len(nits_inconsistentes)))
    tabla.add_row("Reporte", str(reporte) if reporte else "[dim]no generado[/]")
    console.print(tabla)

    if nits_inconsistentes:
        console.print(
            f"\n[bold yellow]⚠ NITs con DV inconsistente: {len(nits_inconsistentes)}[/]"
        )
        for nombre in nits_inconsistentes:
            console.print(f"  [yellow]⚠[/] {nombre}")

    if fallidos:
        console.print("\n[bold yellow]Archivos con error:[/]")
        for nombre, error in fallidos:
            console.print(f"  [red]✗[/] {nombre}: {error}")


def main(argv: Optional[List[str]] = None) -> int:
    """Flujo principal. Devuelve el exit code (0 si procesó al menos una factura)."""
    parser = build_parser()
    args = parser.parse_args(argv)

    # a. Proveedor de IA (valida la API key).
    try:
        proveedor = crear_proveedor(args.provider)
    except ValueError as exc:
        console.print(f"[bold red]Error:[/] {exc}")
        return 2

    # b. Archivos soportados en la carpeta.
    carpeta: Path = args.carpeta
    if not carpeta.is_dir():
        console.print(f"[bold red]Error:[/] la carpeta no existe: {carpeta}")
        return 2

    archivos = _buscar_archivos(carpeta)
    if not archivos:
        console.print(
            f"[bold red]Error:[/] no se encontraron archivos soportados "
            f"({', '.join(EXTENSIONES_SOPORTADAS)}) en {carpeta}"
        )
        return 2

    # c. Procesar cada archivo; los errores NO tumban el lote.
    console.print(f"[bold]Procesando {len(archivos)} archivo(s) de[/] {carpeta}\n")
    facturas: List[Factura] = []
    fallidos: List[Tuple[str, str]] = []
    nits_inconsistentes: List[str] = []
    for archivo in archivos:
        try:
            texto = extraer(archivo)
            factura = proveedor.estructurar_factura(texto, archivo_origen=archivo.name)
            facturas.append(factura)
            # Advertencia de calidad de dato: el DV del NIT no cuadra (no detiene nada).
            if not validar_nit(factura.nit):
                nits_inconsistentes.append(archivo.name)
            console.print(f"  [green]✓[/] {archivo.name} → {factura.categoria.value}")
        except Exception as exc:  # noqa: BLE001 — un archivo no debe tumbar el lote
            fallidos.append((archivo.name, str(exc)))
            console.print(f"  [red]✗[/] {archivo.name}: {exc}")

    # d. Reporte (si al menos una factura salió bien).
    reporte: Optional[Path] = None
    if facturas:
        try:
            reporte = generar_reporte(facturas, args.output)
        except ValueError as exc:
            console.print(f"[bold red]Error al generar el reporte:[/] {exc}")
            return 2

    # e. Resumen.
    console.print()
    _imprimir_resumen(len(facturas), fallidos, nits_inconsistentes, reporte)

    return 0 if facturas else 1


if __name__ == "__main__":
    raise SystemExit(main())
