# Constitución — API Genérica CRUD

> **Documento 1 de 8** del spec kit. Orden de lectura:
> `1_constitution → 2_spec → 3_plan → 4_research → 5_data_model → 6_contracts → 7_quickstart → 8_tasks`.
>
> Principios innegociables de ESTE proyecto tratado como independiente. Si se
> construye dentro del proyecto padre (proyecto_paradigmas), aplica además la
> constitución global en `docs/spec_kit/1_constitution.md` de la raíz.

---

## Artículo 1 — Propósito didáctico

Proyecto para enseñar a estudiantes qué es una API genérica: **un solo conjunto
de endpoints que sirve para cualquier tabla**, sin conocer sus columnas de
antemano. Claridad sobre sofisticación:

- Todo en **español**: código, comentarios, docstrings, mensajes, documentación.
- Cada archivo abre con un docstring que explica su papel.
- El SQL debe quedar **visible** (nada de ORM declarativo que lo esconda).

## Artículo 2 — Genericidad radical

- CERO conocimiento del esquema: ni nombres de tablas ni de columnas en el código.
- Los tipos de columna se descubren en runtime consultando `information_schema`.
- El precio asumido y documentado: sin validación por entidad (eso lo demuestra
  la API de Facturas del proyecto padre), la BD es la única línea de defensa.

## Artículo 3 — Arquitectura en capas estricta

```
HTTP → CONTROLLER (traduce errores a códigos HTTP; no toca SQL)
     → SERVICIO   (valida argumentos, normaliza; ignora HTTP y motor)
     → REPOSITORIO(un dialecto SQL por clase; ignora HTTP)
     → BASE DE DATOS
```

Comunicación entre capas por **interfaces** (`typing.Protocol`); solo la
**fábrica** conoce las clases concretas (Factory + inversión de dependencias).

## Artículo 4 — Independencia del motor

- Motor elegido con `DB_PROVIDER`, jamás con cambios de código.
- Un repositorio por dialecto (PostgreSQL, MySQL/MariaDB, SQL Server); agregar
  un motor = 1 clase + 1 línea en el diccionario de la fábrica.
- Los tres motores se comportan **idéntico** ante la misma petición.

## Artículo 5 — Seguridad en su justa medida académica

- Valores SQL SIEMPRE parametrizados (`:param`); los identificadores van entre
  las comillas del dialecto.
- Contraseñas SIEMPRE como hash BCrypt (costo 12) cuando el cliente lo pide
  (`campos_encriptar`); verificación server-side con `verificar-contrasena`.
- Sin autenticación de la API misma: entorno docente, no producción.

## Artículo 6 — Convenciones fijas

| Cosa | Convención |
|---|---|
| Puerto | **8001** |
| Docs | `/swagger` (docs_url personalizado) y `/redoc`; OpenAPI en `/swagger/v1/swagger.json` |
| Prefijo de rutas | `/api` (tag `Entidades`) |
| Nombres | snake_case en español; clases PascalCase; interfaces `i_`/`I` |
| Sobre de respuesta | `{tabla, esquema, total, datos}` / `{estado, mensaje, …}` — ver 6_contracts.md |
| Errores | `detail = {estado, mensaje, detalle}`; ValueError→400, PermissionError→403, LookupError→404, resto→500 |
