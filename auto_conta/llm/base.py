"""Interfaz abstracta de la capa de IA.

El objetivo es que el proveedor sea intercambiable: hoy Gemini, mañana Claude
u otro. El resto de la aplicación depende SOLO de esta interfaz (`LLMProvider`)
y nunca del SDK concreto, por lo que cambiar de proveedor no toca el pipeline.
"""

from __future__ import annotations

import abc

from auto_conta.models import Factura


class LLMProvider(abc.ABC):
    """Contrato que todo proveedor de IA debe cumplir.

    Una sola responsabilidad: recibir el texto crudo de una factura y devolver
    una `Factura` estructurada y clasificada.
    """

    @abc.abstractmethod
    def estructurar_factura(self, texto: str, archivo_origen: str | None = None) -> Factura:
        """Convierte texto crudo de una factura en un modelo `Factura` validado.

        Args:
            texto: contenido extraído del PDF/Excel.
            archivo_origen: nombre del archivo de origen (para trazabilidad).

        Returns:
            Una instancia de `Factura`.
        """
        raise NotImplementedError


def crear_proveedor(nombre: str = "gemini") -> LLMProvider:
    """Factory simple para instanciar el proveedor por nombre.

    TODO(lote 3): registrar e instanciar GeminiProvider / (futuro) ClaudeProvider.
    """
    raise NotImplementedError("crear_proveedor aún no implementado (FASE 1).")
