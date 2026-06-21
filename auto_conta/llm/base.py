"""Interfaz abstracta de la capa de IA + factory de proveedores.

El objetivo es que el proveedor sea intercambiable: hoy Gemini, mañana Claude
u otro. El resto de la aplicación depende SOLO de esta interfaz (`LLMProvider`)
y nunca del SDK concreto, por lo que cambiar de proveedor no toca el pipeline.
"""

from __future__ import annotations

import abc
import os

from dotenv import load_dotenv

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
    """Instancia el proveedor de IA por nombre.

    Carga `.env` (si existe) y lee GEMINI_API_KEY / GEMINI_MODEL.

    Raises:
        ValueError: si el proveedor no existe o falta la API key.
    """
    load_dotenv()

    if nombre != "gemini":
        raise ValueError(
            f"Proveedor LLM no soportado: '{nombre}'. Disponibles: gemini."
        )

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError(
            "Falta GEMINI_API_KEY. Definila en .env (ver .env.example) o como "
            "variable de entorno."
        )

    # Import diferido para evitar import circular (gemini importa de este módulo).
    from auto_conta.llm.gemini import DEFAULT_MODEL, GeminiProvider

    modelo = os.environ.get("GEMINI_MODEL", DEFAULT_MODEL)
    return GeminiProvider(api_key=api_key, modelo=modelo)
