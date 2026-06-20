# PLAN — auto-conta

Documento vivo. Describe cómo está pensada la herramienta y en qué orden la
vamos a construir. FASE 1 entrega solo el scaffolding (esqueletos y stubs).

---

## 1. Flujo completo, paso a paso

```
carpeta de facturas
        │
        ▼
[1] Descubrir archivos  ──► recorre la carpeta y separa PDF de Excel por extensión
        │
        ▼
[2] Extraer crudo       ──► PDF  -> texto plano (pdfplumber)
                            Excel -> texto/tabla serializada (pandas + openpyxl)
        │
        ▼
[3] Estructurar + clasificar con IA  ──► el texto crudo va a la capa llm/.
                            Gemini devuelve JSON con los campos de la factura
                            y la categoría contable sugerida.
        │
        ▼
[4] Validar con pydantic ──► el JSON se carga en el modelo `Factura`.
                            Si no cumple el esquema, se descarta/marca el error.
        │
        ▼
[5] Consolidar reporte   ──► todas las `Factura` válidas -> DataFrame ->
                            export a Excel (.xlsx) o CSV.
```

### Detalle por paso

1. **Descubrimiento** (`cli.py`): recibe la carpeta, lista archivos `.pdf`,
   `.xlsx`/`.xls` y los enruta al extractor correspondiente.
2. **Extracción** (`extractors/`): convierte cada archivo en texto que la IA
   pueda leer. No interpreta, solo extrae.
3. **IA** (`llm/`): un único método `estructurar_factura(texto)` que devuelve
   un objeto `Factura`. Aquí vive el prompt y la llamada al proveedor.
4. **Validación** (`models.py`): pydantic garantiza tipos, campos obligatorios
   (proveedor, total) y normaliza valores (`Decimal`, fechas, categoría enum).
5. **Reporte** (`report.py`): aplana las facturas a filas y exporta el
   consolidado que usará contabilidad.

---

## 2. Librería usada en cada paso y por qué

| Paso | Librería | Por qué |
|------|----------|---------|
| Leer PDF | **pdfplumber** | Extrae texto (y tablas) de PDF con buena fidelidad de layout, mejor que PyPDF2 para facturas con columnas. |
| Leer Excel | **pandas** + **openpyxl** | pandas modela las tablas con poco código; openpyxl es el motor para `.xlsx`. |
| IA generativa | **google-genai** (`from google import genai`) | SDK unificado/oficial de Gemini (reemplaza al deprecado `google-generativeai`); soporta salida estructurada/JSON. |
| Validación | **pydantic** | Esquema declarativo, validación de tipos y parsing automático de la respuesta del modelo. |
| Reporte | **pandas** + **openpyxl** | Reusa pandas para volcar a `.xlsx`/`.csv` en una línea. |
| Config / secretos | **python-dotenv** | Carga `GEMINI_API_KEY` desde `.env` sin hardcodear. |
| Consola | **rich** | Tablas, progreso y mensajes de error legibles en la CLI. |
| Pruebas | **pytest** | Estándar de facto para tests en Python. |

---

## 3. Diseño de la capa `llm/` (proveedor intercambiable)

La regla de oro: **el pipeline depende de una interfaz, no de un SDK**.

- `llm/base.py` define `LLMProvider`, una clase abstracta con un único método:
  `estructurar_factura(texto, archivo_origen) -> Factura`.
- `llm/gemini.py` implementa `GeminiProvider(LLMProvider)` usando el SDK nuevo
  `google-genai` (`from google import genai`, `genai.Client(...)`).
- Un **futuro** `llm/claude.py` implementaría `ClaudeProvider(LLMProvider)` con
  el SDK de Anthropic, sin tocar el resto del código.
- `crear_proveedor(nombre)` es una *factory* que devuelve la implementación
  correcta según el flag `--proveedor-llm` de la CLI.

```
            ┌─────────────────────────┐
 pipeline ─►│ LLMProvider (abstracta) │  ◄── única dependencia del resto del código
            └────────────┬────────────┘
                         │ implementan
              ┌──────────┴──────────┐
              ▼                     ▼
      GeminiProvider          ClaudeProvider (futuro)
      (google-genai)             (anthropic)
```

Ventaja: cambiar de Gemini a Claude = agregar una clase + una entrada en la
factory. El extractor, los modelos y el reporte no se enteran.

---

## 4. Categorías contables iniciales

Set razonable de arranque (enum `CategoriaContable` en `models.py`), ampliable:

- `servicios_publicos` — luz, agua, gas, internet, telefonía.
- `papeleria` — útiles e insumos de oficina.
- `arriendo` — alquiler de inmuebles/locales.
- `transporte` — fletes, taxis, combustible, logística.
- `tecnologia` — software, hardware, suscripciones SaaS.
- `honorarios` — servicios profesionales, consultorías.
- `mantenimiento` — reparaciones y aseo.
- `alimentacion` — comidas, cafetería, eventos.
- `marketing` — publicidad y promoción.
- `impuestos` — tasas y tributos.
- `otros` — categoría por defecto / fallback.

---

## 5. Orden de construcción por lotes

- **Lote 0 — Scaffolding (FASE 1, actual)**: estructura, stubs, modelos,
  interfaz `LLMProvider`, PLAN y dependencias instaladas.
- **Lote 1 — Modelos + samples**: afinar `models.py` y generar facturas
  sintéticas en `samples/` (PDF y Excel) para probar sin datos reales.
- **Lote 2 — Extractores**: implementar `pdf_extractor` y `excel_extractor`
  con tests unitarios contra los samples.
- **Lote 3 — Capa IA (Gemini)**: prompt, llamada a Gemini, parseo a `Factura`
  y la factory `crear_proveedor`.
- **Lote 4 — Reporte**: `generar_reporte` a Excel/CSV con pandas.
- **Lote 5 — CLI end-to-end**: conectar todo en `cli.py procesar`, manejo de
  errores y salida con rich.
- **Lote 6 — Robustez**: validaciones, casos borde, cobertura de tests y
  (opcional) `ClaudeProvider`.
