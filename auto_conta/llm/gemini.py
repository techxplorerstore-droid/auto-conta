"""Proveedor de IA basado en Google Gemini, usando el SDK `google-genai`.

Convierte el texto crudo de una factura (ya extraído por la capa `extractors`)
en un modelo `Factura` validado y clasificado.

Patrón del SDK (google-genai v2.x):
    from google import genai
    client = genai.Client(api_key=...)
    resp = client.models.generate_content(
        model=..., contents=..., config=GenerateContentConfig(
            response_mime_type="application/json", response_schema=Factura,
        ),
    )

Manejo de Decimal: se valida `response.text` con `Factura.model_validate_json`,
que en pydantic v2 parsea los números directamente desde el token JSON a
`Decimal` (sin pasar por float), preservando la precisión tanto si el modelo
devuelve números como strings.
"""

from __future__ import annotations

import os

from google import genai
from google.genai import types

from auto_conta.llm.base import LLMProvider
from auto_conta.models import CategoriaContable, Factura

DEFAULT_MODEL = "gemini-2.5-flash"

_CATEGORIAS = ", ".join(c.value for c in CategoriaContable)

_PROMPT = """Eres un asistente contable experto en facturas colombianas.

A partir del TEXTO de una factura, extrae los datos y devuélvelos en JSON con
esta semántica:
- numero_factura, proveedor (razón social), nit, fecha (formato YYYY-MM-DD).
- moneda: código ISO (usa "COP" si no se indica).
- items: lista con descripcion, cantidad, valor_unitario y valor_total.
- subtotal, iva_porcentaje (p. ej. 19), iva_valor y total.
- categoria: clasifica el gasto en EXACTAMENTE uno de estos valores: {categorias}.
  Si ninguno encaja con claridad, usa "otros".

Reglas:
- No inventes datos: si un valor no aparece, infiérelo solo cuando sea evidente.
- Los montos son numéricos, sin símbolo de moneda ni separadores de miles.

TEXTO DE LA FACTURA:
{texto}
"""


def _limpiar_json(texto: str) -> str:
    """Quita fences de código (```json ... ```) si el modelo los agrega."""
    t = texto.strip()
    if t.startswith("```"):
        t = t[3:]
        if t[:4].lower() == "json":
            t = t[4:]
        if t.endswith("```"):
            t = t[:-3]
    return t.strip()


class GeminiProvider(LLMProvider):
    """Proveedor de IA basado en Gemini (SDK `google-genai`)."""

    def __init__(self, api_key: str | None = None, modelo: str = DEFAULT_MODEL) -> None:
        api_key = api_key or os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError(
                "Falta GEMINI_API_KEY para instanciar GeminiProvider."
            )
        self.modelo = modelo
        self.client = genai.Client(api_key=api_key)

    def estructurar_factura(self, texto: str, archivo_origen: str | None = None) -> Factura:
        prompt = _PROMPT.format(categorias=_CATEGORIAS, texto=texto)
        response = self.client.models.generate_content(
            model=self.modelo,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=Factura,
            ),
        )
        factura = self._a_factura(response)
        factura.archivo_origen = archivo_origen
        return factura

    @staticmethod
    def _a_factura(response: object) -> Factura:
        """Convierte la respuesta del SDK en una `Factura` validada.

        Prefiere `response.text` (parseo a Decimal sin pérdida de precisión);
        cae a `response.parsed` si no hay texto.
        """
        texto = getattr(response, "text", None)
        if texto:
            return Factura.model_validate_json(_limpiar_json(texto))

        parsed = getattr(response, "parsed", None)
        if isinstance(parsed, Factura):
            return parsed
        if parsed is not None:
            return Factura.model_validate(parsed)

        raise ValueError("La respuesta de Gemini no contiene datos parseables.")
