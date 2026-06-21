# AutoConta

Herramienta de línea de comandos que automatiza la extracción y categorización de datos contables desde facturas en PDF y Excel usando IA generativa (Google Gemini). Le pasás una carpeta de facturas y devuelve un reporte consolidado en Excel o CSV con el gasto agrupado por categoría.

## Pipeline

Carpeta de facturas (PDF/Excel) → extracción de texto → estructuración con IA → validación → reporte consolidado.

1. **Extracción** — `pdfplumber` (PDF) y `openpyxl` (Excel) extraen el texto crudo de cada factura. Devuelven solo texto: no parsean, para no depender de parsers frágiles por cada layout.
2. **Estructuración con IA** — Gemini (`google-genai`) recibe el texto y devuelve los datos estructurados (proveedor, NIT, fecha, ítems, subtotal, IVA, total) y clasifica el gasto en una categoría contable, usando salida estructurada (`response_schema`) validada contra un modelo `pydantic`.
3. **Reporte** — `pandas` consolida las facturas en un Excel de dos hojas (detalle + resumen por categoría) o un CSV.

Los errores se aíslan por archivo: si una factura falla, se registra y el proceso continúa con las demás.

## Stack

- Python 3.12
- google-genai (Gemini 2.5 Flash por defecto, configurable vía `GEMINI_MODEL`)
- pydantic v2 (validación; `Decimal` para precisión en montos)
- pdfplumber, openpyxl, pandas
- rich (salida en terminal)
- pytest (tests)

## Instalación

```bash
git clone https://github.com/techxplorerstore-droid/auto-conta.git
cd auto-conta
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Configurá tu API key de Gemini:

```bash
cp .env.example .env
# editá .env y poné tu GEMINI_API_KEY
```

## Uso

```bash
python -m auto_conta <carpeta> -o reporte.xlsx
```

- `<carpeta>` — carpeta con las facturas (.pdf, .xlsx, .xls)
- `-o, --output` — ruta del reporte (.xlsx o .csv; default `reporte.xlsx`)
- `--provider` — proveedor de IA (default `gemini`)

Ejemplo sobre las facturas de muestra incluidas:

```bash
python -m auto_conta samples -o reporte.xlsx
```

## Ejemplo de salida

```
Procesando 7 archivo(s) de samples

  ✓ factura_arriendo.pdf → arriendo
  ✓ factura_energia.pdf → servicios_publicos
  ✓ factura_honorarios.xlsx → honorarios
  ✓ factura_mantenimiento.xlsx → mantenimiento
  ✓ factura_papeleria.pdf → papeleria_oficina
  ✓ factura_tecnologia.pdf → tecnologia
  ✓ factura_transporte.pdf → transporte

               Resumen
┏━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┓
┃ Métrica             ┃        Valor ┃
┡━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━┩
│ Facturas procesadas │            7 │
│ Facturas fallidas   │            0 │
│ Total de archivos   │            7 │
│ Reporte             │ reporte.xlsx │
└─────────────────────┴──────────────┘
```

El `reporte.xlsx` tiene dos hojas:
- **Facturas** — una fila por factura: proveedor, NIT, fecha, categoría, subtotal, IVA y total.
- **Resumen** — gasto agrupado por categoría con total general.

## Categorías contables

`servicios_publicos`, `papeleria_oficina`, `arriendo`, `transporte`, `tecnologia`, `mantenimiento`, `honorarios`, `otros`.

## Tests

```bash
pip install -r requirements-dev.txt
pytest
```

Los tests unitarios corren sin red (cliente de Gemini mockeado). Hay un test de integración que llama a la API real y se salta automáticamente si no hay `GEMINI_API_KEY` configurada.

## Diseño

- La capa LLM es intercambiable (interfaz `LLMProvider`): hoy Gemini, con Claude como proveedor previsto.
- Los montos usan `Decimal` para precisión contable; el Excel los muestra como números para que sean sumables.

## Validación y calidad de datos

- **NIT**: los NIT se normalizan a una forma canónica determinística (`<base>-<DV>`, sin puntos) y se validan contra el dígito de verificación de la DIAN (módulo 11). Un NIT con DV inconsistente se marca como advertencia en el resumen, sin descartar el dato (un DV malo no tumba una extracción por lo demás correcta).
- **Montos**: usan `Decimal` para precisión contable, evitando los errores de redondeo del punto flotante.

## Roadmap / Limitaciones conocidas

- Proveedor Claude (anthropic) como alternativa a Gemini.
- Soporte para más layouts de factura y procesamiento por lotes más grande.

## Nota

Las facturas de `samples/` son sintéticas (datos 100% ficticios). La herramienta no debe usarse con datos reales de clientes sin las consideraciones de privacidad correspondientes.
