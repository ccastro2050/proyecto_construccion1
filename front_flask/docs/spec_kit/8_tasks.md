# Tareas — Frontend Flask

> **Documento 8 de 8** del spec kit: el orden de construcción. Cada fase termina
> en algo **verificable**. Requisitos: [2_spec.md](2_spec.md) · técnica:
> [3_plan.md](3_plan.md) · contratos: [6_contracts.md](6_contracts.md) ·
> validación final: [7_quickstart.md](7_quickstart.md).
> Prerrequisito: al menos una de las dos APIs corriendo en
> `localhost:8001`/`localhost:8002` (cualquier implementación que cumpla los
> contratos de [6_contracts.md](6_contracts.md) §2).

---

## Fase 0 — Esqueleto
- [ ] Carpetas `rutas/`, `servicios/`, `static/`, `templates/` con `__init__.py`
      donde corresponde.
- [ ] `requirements.txt` (flask, requests) + entorno virtual.
- [ ] `config.py` con las 3 constantes y sus defaults localhost.

## Fase 1 — Cliente HTTP
- [ ] `servicios/cliente_api.py`: clase `ClienteApi` completa
      (constructor, `_url_listar`, `_url_registro`, 5 métodos CRUD, `estado()`,
      `_mensaje_error`).

**Verificar:** en un REPL con las APIs arriba:
`ClienteApi("generica").listar("producto")` → `(True, [8 dicts])`;
`ClienteApi("facturas").listar("producto")` → igual;
con las APIs apagadas → `(False, "No se pudo conectar…")`.

## Fase 2 — App base + inicio
- [ ] `app.py`: app, secret_key, context processor `api_activa`, ruta
      `/cambiar-api/<nombre>`, registro del blueprint de inicio.
- [ ] `templates/base.html` (navbar, dropdown de API, flashes, footer).
- [ ] `rutas/inicio.py` + `templates/inicio.html` (diagrama, 2 tarjetas con
      badge según `estado()`, botones Swagger y "Usar esta API").
- [ ] `static/estilos.css` (3 reglas).

**Verificar:** `flask --app app run --port 8000 --debug` →
la página muestra los badges correctos (probar apagando una API);
el dropdown cambia `API: Genérica ↔ Facturas` y la opción queda `active`.

## Fase 3 — CRUD de productos (el molde)
- [ ] `rutas/productos.py` (listar, crear GET/POST, editar GET/POST, eliminar POST).
- [ ] `templates/productos_lista.html` y `productos_formulario.html`.
- [ ] Registrar el blueprint en `app.py`.

**Verificar:** ciclo completo crear PR009 → editar → eliminar con sus flashes;
formato `$ 2,500,000` en la lista; con la API apagada la lista muestra el error
y no revienta.

## Fase 4 — CRUD de personas (replicar el molde)
- [ ] `rutas/personas.py` + sus 2 templates (campos codigo/nombre/email/telefono).
- [ ] Alerta didáctica de integridad referencial en la lista.

**Verificar:** crear/editar/eliminar P007; eliminar P001 → alerta roja con el
error de llave foránea textual.

## Fase 5 — Facturas (maestro-detalle, solo lectura)
- [ ] `rutas/facturas.py`: lista y detalle con el filtrado en Python documentado.
- [ ] `templates/facturas_lista.html` (badge estado) y `facturas_detalle.html`
      (breadcrumb, tarjeta maestro, tabla de renglones, alerta sobre triggers).

**Verificar:** `/facturas/1` muestra maestro + renglones; fecha `YYYY-MM-DD HH:MM:SS`;
una factura sin detalle muestra "Esta factura no tiene detalle.".

## Fase 6 — Explorador
- [ ] `rutas/explorador.py` (constante `TABLAS`, tabla default `persona`,
      columnas dinámicas) + `templates/explorador.html` (select con auto-submit,
      encabezado con la API usada).

**Verificar:** recorrer las 12 tablas; el select conserva la selección;
cambiar de API y comprobar que el encabezado lo refleja.

## Fase 7 — Ambas APIs y pulido
- [ ] Probar TODAS las pantallas con la API Facturas activa
      (la barra final de `_url_listar` es lo que suele fallar aquí).
- [ ] Repasar comentarios didácticos en código y plantillas (plan §4.6).

## Fase 8 — Docker
- [ ] `Dockerfile` del plan (§5).
- [ ] Alta en el compose raíz: servicio `front`, puerto 8000, volumen de código,
      `command` con `--debug`, variables `API_GENERICA_URL`/`API_FACTURAS_URL`
      con hosts internos.

**Verificar:** `docker compose up -d --build` desde la raíz → los 7 criterios de
aceptación de [2_spec.md](2_spec.md) §5 pasan; editar un `.py` recarga la app sola.
