# Front Flask — interfaz web del proyecto

Frontend en **Flask** (puerto **8010**): la capa de presentación que consume
las dos APIs Python del proyecto — la **Genérica** (8011) y la **Facturas**
(8012) — y permite cambiar entre ellas en caliente desde el menú, para
demostrar que ambas cumplen el mismo contrato.

- **En Docker (lo normal):** sube con todo el sistema desde la raíz del
  proyecto — `docker compose up -d --build`. El código está montado como
  volumen y corre con `--debug`: guardar un `.py` o un `.html` recarga solo.
- **Solo (sin Docker):** `flask --app app run --port 8010 --debug` con las
  APIs corriendo en localhost.
- **Spec kit propio:** en [docs/spec_kit/](docs/spec_kit/) están los 8
  documentos con los que este front se reconstruye desde cero, sin leer el
  resto del proyecto.

## Estructura del proyecto

Qué es cada carpeta y cada archivo, y para qué sirve:

```
front_flask/
├── app.py                        # Punto de entrada: crea la app, registra los
│                                 #   blueprints y la ruta /cambiar-api/<nombre>
├── config.py                     # Las URLs de las 2 APIs (env con default localhost)
├── requirements.txt              # Dependencias: flask + requests
├── Dockerfile                    # Imagen python:3.12-slim para el compose
│
├── rutas/                        # Un blueprint por pantalla (la capa "controller")
│   ├── inicio.py                 #   Estado de las 2 APIs + tarjetas de selección
│   ├── productos.py              #   CRUD completo de producto (el molde)
│   ├── personas.py               #   CRUD de persona (replica el molde)
│   ├── facturas.py               #   Facturas: lista y maestro-detalle (solo lectura)
│   └── explorador.py             #   Tabla dinámica: recorre las 12 tablas
│
├── servicios/
│   └── cliente_api.py            # ClienteApi: el ÚNICO lugar que habla HTTP con
│                                 #   las APIs (elige la base según la API activa,
│                                 #   nunca lanza excepciones hacia las rutas)
│
├── templates/                    # HTML con Jinja2 + Bootstrap 5
│   ├── base.html                 #   Layout: navbar, dropdown de API, flashes
│   ├── inicio.html               #   Portada con las 2 tarjetas de estado
│   ├── productos_lista.html      #   Cada CRUD usa el par lista + formulario
│   ├── productos_formulario.html #
│   ├── personas_lista.html       #
│   ├── personas_formulario.html  #
│   ├── facturas_lista.html       #   Facturas con estado como badge
│   ├── facturas_detalle.html     #   Maestro (factura) + detalle (renglones)
│   └── explorador.html           #   Select de tabla con auto-submit
│
├── static/
│   └── estilos.css               # Los pocos estilos propios (el resto es Bootstrap)
│
└── docs/
    └── spec_kit/                 # Spec kit AUTOCONTENIDO (documentos 1 a 8):
                                  #   con esta carpeta se reconstruye el front desde cero
```

La regla de lectura: una petición entra por un blueprint de `rutas/`, este
usa `servicios/cliente_api.py` para hablar con la API activa, y pinta el
resultado con un template de `templates/`. Tres carpetas, tres
responsabilidades — la misma separación por capas que el resto del proyecto.
