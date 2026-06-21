"""Permite ejecutar el paquete con `python -m auto_conta`."""

from __future__ import annotations

import sys

from auto_conta.cli import main

if __name__ == "__main__":
    sys.exit(main())
