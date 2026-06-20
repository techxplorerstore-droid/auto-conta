"""Implementación del proveedor de IA usando Google Gemini.

FASE 1: solo stub. Usa el SDK unificado nuevo `google-genai`
(`from google import genai`), que reemplaza al deprecado `google-generativeai`.

Patrón del SDK nuevo:
    from google import genai
    client = genai.Client(api_key=...)
    resp = client.models.generate_content(model=MODEL, contents=...)

La implementación real leerá GEMINI_API_KEY del entorno y pedirá una salida
JSON que se valida contra el modelo `Factura` de pydantic.
"""

from __future__ import annotations

import os

from google import genai

from auto_conta.llm.base import LLMProvider
from auto_conta.models import Factura

# definir modelo estable en el lote de LLM
MODEL = ""


class GeminiProvider(LLMProvider):
    """Proveedor de IA basado en Gemini (SDK `google-genai`)."""

    def __init__(self, api_key: str | None = None, modelo: str = MODEL) -> None:
        # TODO(lote 3): instanciar el cliente con la API key real.
        #   self.client = genai.Client(api_key=api_key or os.environ["GEMINI_API_KEY"])
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        self.modelo = modelo
        self.client: genai.Client | None = None

    def estructurar_factura(self, texto: str, archivo_origen: str | None = None) -> Factura:
        # TODO(lote 3): construir prompt, llamar al modelo y parsear JSON -> Factura.
        #   resp = self.client.models.generate_content(
        #       model=self.modelo, contents=prompt,
        #   )
        #   return Factura.model_validate_json(resp.text)
        raise NotImplementedError("GeminiProvider aún no implementado (FASE 1).")
