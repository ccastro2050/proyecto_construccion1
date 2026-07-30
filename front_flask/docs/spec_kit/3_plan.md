# Plan técnico — Frontend Flask

> **Documento 3 de 8** del spec kit: **CÓMO** construir lo especificado en
> [2_spec.md](2_spec.md). El porqué de cada decisión: [4_research.md](4_research.md) ·
> contratos con las APIs: [6_contracts.md](6_contracts.md) · orden: [8_tasks.md](8_tasks.md).

---

## 1. Stack

| Pieza | Elección | Por qué |
|---|---|---|
| Framework | Flask ≥ 3.0 | Mínimo, didáctico, blueprints |
| Cliente HTTP | requests ≥ 2.31 (síncrono) | Suficiente para un front server-side |
| Plantillas | Jinja2 (incluido en Flask) | Herencia de plantillas |
| Estilos | Bootstrap 5.3.3 + Bootstrap Icons 1.11.3 por **CDN** | Cero build step; el CSS propio son 3 reglas |
| Imagen | python:3.12-slim | Sin drivers de BD: la imagen es trivial |

Sin python-dotenv, sin gunicorn, sin flask-wtf, sin JS propio.

## 2. Estructura de archivos

```
front_flask/
├── Dockerfile                # slim + pip install + CMD flask run --port 8000
├── requirements.txt          # flask, requests
├── config.py                 # 3 constantes con os.getenv()
├── app.py                    # crea app, registra blueprints, /cambiar-api, context processor
├── rutas/                    # un blueprint por sección
│   ├── inicio.py             # GET /
│   ├── productos.py          # CRUD — EL EJEMPLO GUÍA
│   ├── personas.py           # CRUD — réplica del patrón
│   ├── facturas.py           # solo lectura, maestro-detalle
│   └── explorador.py         # tabla dinámica
├── servicios/
│   └── cliente_api.py        # clase ClienteApi (único lugar con requests)
├── static/
│   └── estilos.css           # .tarjeta-api hover + thead versalitas
└── templates/
    ├── base.html             # navbar + selector API + flash + bloque contenido + footer
    ├── inicio.html
    ├── productos_lista.html      / productos_formulario.html
    ├── personas_lista.html       / personas_formulario.html
    ├── facturas_lista.html       / facturas_detalle.html
    └── explorador.html
```

## 3. Piezas clave

### 3.1 config.py — módulo plano
```python
API_GENERICA_URL = os.getenv("API_GENERICA_URL", "http://localhost:8001")
API_FACTURAS_URL = os.getenv("API_FACTURAS_URL", "http://localhost:8002")
SECRET_KEY       = os.getenv("SECRET_KEY", "clave-de-desarrollo-paradigmas")
```
Defaults para correr sin Docker; en compose llegan los hosts internos
`http://api-generica:8001` / `http://api-facturas:8002`.

### 3.2 app.py
- App global (`app = Flask(__name__)`), NO application factory. `app.secret_key = config.SECRET_KEY`.
- Registra los 5 blueprints (cada uno trae su `url_prefix`).
- Context processor `inyectar_api_activa()` → `{"api_activa": session.get("api", "generica")}`.
- Ruta `GET /cambiar-api/<nombre>`: whitelist `("generica", "facturas")` →
  `session["api"] = nombre` → `redirect(request.referrer or url_for("inicio.pagina_inicio"))`.
- Sin errorhandlers, sin `if __name__ == "__main__"` (arranque por CLI de Flask).

### 3.3 ClienteApi (servicios/cliente_api.py)
- `ClienteApi(nombre_api)`: `"facturas"` → `url_base = API_FACTURAS_URL`; cualquier
  otro valor → genérica (fail-safe). Se instancia **por petición** en cada ruta con
  el helper `_api() → ClienteApi(session.get("api", "generica"))`.
- Dos helpers privados encapsulan la ÚNICA diferencia entre APIs:
  - `_url_listar(tabla)`: genérica sin barra final; facturas CON barra final
    (sus routers declaran `GET /` dentro del prefix).
  - `_url_registro(tabla, clave, valor)`: genérica `/{tabla}/{clave}/{valor}`;
    facturas `/{tabla}/{valor}`.
- Métodos públicos (todos devuelven `(exito: bool, resultado)`):
  `listar(tabla)` (204→`(True, [])`), `obtener(tabla, clave, valor)` (devuelve
  `datos[0]`), `crear(tabla, datos)`, `actualizar(tabla, clave, valor, datos)`,
  `eliminar(tabla, clave, valor)`, y `estado()` → JSON de `GET {base}/` o `None`.
- Timeouts: 10 s CRUD, 5 s estado. Esqueleto común:
  `try → requests.<verbo>(...) → raise_for_status() → except RequestException → (False, _mensaje_error(e))`.
- `_mensaje_error(e)` (staticmethod): extrae `detail` del JSON de FastAPI;
  si es dict prioriza `detalle`, luego `mensaje`; si no hay JSON → `Error HTTP {status}`;
  sin respuesta → `No se pudo conectar con la API: {e}`.

### 3.4 Blueprints
Convención: variable `bp_<nombre>`, nombre interno sin prefijo
(`Blueprint("productos", __name__, url_prefix="/productos")`), constantes de
módulo `TABLA` y `CLAVE`.

**productos.py** (molde a replicar):
- `GET /` listar → si falla: `flash(resultado, "danger")` + lista vacía.
- `GET|POST /nuevo`: POST lee `request.form` (`codigo`/`nombre` con `.strip()`,
  `stock` int, `valorunitario` float) → flash + redirect a listar si éxito.
- `GET|POST /editar/<codigo>`: GET obtiene y repobla; POST arma datos con
  `"codigo": codigo` del path (el input va `disabled` y no viaja en el form).
- `POST /eliminar/<codigo>`: siempre flash + redirect.

**personas.py**: idéntico con campos codigo/nombre/email/telefono (todos str).

**facturas.py**: `GET /` lista; `GET /<int:numero>` hace DOS llamadas —
`obtener("factura", "numero", numero)` + `listar("productosporfactura")` — y
filtra en Python `[d for d in todos if d.get("fknumfactura") == numero]`
(el converter `int:` importa: la comparación es entero contra entero).

**explorador.py**: constante `TABLAS` (las 12), `tabla = request.args.get("tabla", "persona")`,
`columnas = list(filas[0].keys()) if filas else []`.

**inicio.py**: llama `ClienteApi("generica").estado()` y `ClienteApi("facturas").estado()`
(ambas fijas, ignora la API activa) y pasa `estado_generica`/`estado_facturas`.

### 3.5 Templates
- `base.html`: `<html lang="es">`; bloques Jinja en español (`{% block titulo %}`,
  `{% block contenido %}`); navbar `navbar-dark bg-dark` con los 4 enlaces
  (íconos `bi-box-seam`, `bi-people`, `bi-receipt`, `bi-table`); dropdown del
  selector de API a la derecha (`btn-outline-info`, opciones "API Genérica
  (puerto 8001)" / "API Facturas (puerto 8002)" con clase `active` según
  `api_activa`); zona de flashes `alert-{{ categoria }} alert-dismissible`;
  footer oscuro con el diagrama de puertos; `bootstrap.bundle.min.js` al final.
  Sticky footer con `body.d-flex.flex-column.min-vh-100` + `main.flex-grow-1`.
- Listas: `card > table-responsive > table table-striped table-hover`,
  `thead table-dark`, `{% for %}…{% else %}` para el estado vacío, formato de
  moneda `$ {{ "{:,.0f}".format(x | float) }}`, eliminar SIEMPRE con
  `<form method="post">` + `onsubmit="return confirm('…')"` (nunca un enlace GET).
- Formularios: plantilla compartida crear/editar (`producto=None` ⇒ crear);
  PK `disabled` en edición, `required` en creación; validación por atributos
  HTML (`maxlength`, `min`, `step`, `type=email/number`).
- Sin macros ni includes; cada plantilla autocontenida y comentada con `{# … #}`.

### 3.6 estilos.css (3 reglas, nada más)
`.tarjeta-api` con transición + hover elevado; `table thead th` en versalitas
(`font-size .85rem; text-transform: uppercase; letter-spacing: .03em`).

## 4. Patrones obligatorios

1. **Separación estricta**: ruta → ClienteApi → API. Nada de `requests` fuera de
   `cliente_api.py`; nada de SQL en el front.
2. **Contrato `(exito, resultado)`**: el cliente nunca lanza; la ruta decide el flash.
3. **Post→Redirect→Get** tras toda escritura.
4. **Solo categorías de flash `success` y `danger`** (mapean a clases Bootstrap).
5. **Degradación elegante**: error de API = flash + vista vacía.
6. **Comentarios didácticos**: docstring de módulo con bloques "CONCEPTO — …",
   separadores `# ====`, secciones `# READ — Listar`, `# CREATE — Crear`…,
   trato de usted al lector, invitaciones a experimentar en alerts de la UI.

## 5. Dockerfile y compose

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["flask", "--app", "app", "run", "--host", "0.0.0.0", "--port", "8000"]
```
En compose: puerto `8000:8000`, volumen `./front_flask:/app` (+ `.:/workspace:cached`
para el devcontainer), `command` con `--debug`, y las dos variables `API_*_URL`.
