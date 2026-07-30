# Quickstart — Frontend Flask

> **Documento 7 de 8** del spec kit. Validación rápida del front ya construido.
> Si aún no hay nada construido, empiece por [8_tasks.md](8_tasks.md).

---

## 1. Prerrequisito: al menos una API arriba

Lo ideal: `docker compose up -d` en la raíz del proyecto padre (levanta las dos
APIs con su BD). Alternativa mínima: la API Genérica sola contra un PostgreSQL
suelto (ver su propio spec kit).

## 2. Arrancar el front

```powershell
# local (desde front_flask, con el venv activo; las APIs en localhost)
flask --app app run --port 8000 --debug
```

(En Docker: `docker build -t front-flask . ; docker run -p 8000:8000 -e API_GENERICA_URL=... -e API_FACTURAS_URL=... front-flask`.)

## 3. Recorrido de validación (5 minutos, en el navegador)

1. **http://localhost:8000** → las dos tarjetas con badge **"en línea"** verde.
   Apague una API (`docker compose stop api-generica`) y recargue → badge rojo
   "sin conexión". Vuélvala a subir.
2. **Productos** → crear `PR009 / Webcam / 5 / 120000` → flash verde y aparece
   en la tabla con `$ 120,000` → editar el stock a 7 → eliminar con el
   `confirm()` → flash verde en cada paso.
3. **Selector de API** (menú superior derecho) → "API Facturas (puerto 8002)" →
   repetir el paso 2: **todo funciona igual** (esa es la tesis). Cree un
   producto sin nombre desde la API Facturas: la validación Pydantic del
   backend llega como alerta roja.
4. **Personas** → intentar eliminar `P001` → alerta roja con el error de llave
   foránea textual de la BD (P001 es cliente).
5. **Facturas** → lista con estados como badge → entrar a la factura 1 →
   maestro (fecha `YYYY-MM-DD HH:MM:SS`, total verde) + renglones del detalle.
6. **Explorador** → recorrer varias de las 12 tablas; el encabezado dice con
   cuál API se consultó; una tabla vacía muestra "Tabla vacía.".
7. Apague las dos APIs y navegue: cada pantalla muestra su flash de error y el
   sitio sigue navegable (nunca un traceback).

## 4. Si algo falla

| Síntoma | Causa probable |
|---|---|
| Badges rojos con las APIs corriendo | `API_*_URL` mal apuntadas (¿localhost vs nombre de servicio Docker?) |
| Listas vacías + flash "No se pudo conectar" | API caída o puerto equivocado |
| Con Facturas activa todo falla, con Genérica no | Falta la **barra final** en `_url_listar` para facturas |
| El selector no "pega" | `SECRET_KEY` cambió entre requests (sesión invalidada) o cookie bloqueada |
| Los estilos no cargan | Sin internet: Bootstrap viene por CDN |
| 500 al crear producto | `stock`/`valorunitario` no numéricos llegaron al `int()`/`float()` (brecha aceptada, research D9) |
