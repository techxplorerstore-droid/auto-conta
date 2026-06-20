# auto-conta

Herramienta CLI que automatiza la extracción y categorización de datos contables
desde facturas en **PDF** y **Excel**, usando IA generativa (**Gemini**) para
estructurar y clasificar la información.

> Estado: 🚧 FASE 1 — scaffolding. La lógica de las features se construye por lotes.

## ¿Qué hace?

1. Toma una carpeta con facturas (PDF y/o Excel).
2. Extrae el texto/datos crudos de cada archivo.
3. Usa IA para estructurar los campos clave (proveedor, NIT, fecha, subtotal,
   IVA, total, ítems) y clasificar el gasto en una categoría contable.
4. Valida el resultado con modelos pydantic.
5. Consolida todo en un único reporte Excel/CSV.

## Stack

- **pdfplumber** — extracción de texto de PDF.
- **pandas** + **openpyxl** — lectura de Excel y generación del reporte.
- **google-genai** — capa de IA (Gemini), intercambiable.
- **pydantic** — validación y modelado de datos.
- **python-dotenv** — manejo de variables de entorno / API keys.
- **rich** — salida en consola.
- **pytest** — pruebas.

## Instalación

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # y completá GEMINI_API_KEY
```

## Uso

> ⏳ Pendiente de implementación (FASE 1). La interfaz prevista:

```bash
auto-conta procesar ./samples --salida reporte.xlsx
```

## Estructura

Ver [PLAN.md](PLAN.md) para el flujo completo, el diseño de la capa de IA,
las categorías contables y el orden de construcción por lotes.
