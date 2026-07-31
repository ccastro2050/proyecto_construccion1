# Tareas — Infraestructura e integración

> **Documento 8 de 8** del spec kit raíz: orden de construcción del proyecto
> completo. Cada fase termina en algo **verificable**.
> Requisitos: [2_spec.md](2_spec.md) · decisiones: [3_plan.md](3_plan.md) ·
> principios: [1_constitution.md](1_constitution.md) · BD: [5_data_model.md](5_data_model.md) ·
> integración: [6_contracts.md](6_contracts.md) · verificación: [7_quickstart.md](7_quickstart.md).

---

## Fase 0 — Repositorio
- [ ] `git init`, `.gitignore` (venv, `__pycache__`, `.env*`), `README.md` inicial.
- [ ] Crear carpetas `db/postgres`, `db/mariadb`, `db/sqlserver`, `docs/`.

## Fase 1 — La base de datos en PostgreSQL (el motor guía)
- [ ] Escribir `db/postgres/init.sql`: 12 tablas en orden de dependencias, datos de
      ejemplo, `setval` de secuencias, trigger `actualizar_totales_y_stock`, y los
      SP de facturas/usuarios/RBAC (plan §3).
- [ ] Servicio `postgres` en un `docker-compose.yml` mínimo (imagen 16-alpine,
      volumen `pgdata`, init.sql montado, puerto 15432, healthcheck).

**Verificar:** `docker compose up -d postgres` → conectar con pgAdmin/psql a
localhost:15432 y comprobar: 12 tablas, 8 productos; insertar un renglón en
`productosporfactura` recalcula subtotal, stock y total (trigger);
`CALL sp_consultar_factura_y_productosporfactura(1, NULL)` devuelve JSON.

## Fase 2 — Los otros dos motores
- [ ] Traducir el script a `db/mariadb/init.sql` (DROP IF EXISTS + utf8mb4 + DELIMITER).
- [ ] Traducir a `db/sqlserver/bdfacturas.sql` (T-SQL) y escribir `db/sqlserver/init.sh`.
- [ ] Agregar servicios `mariadb`, `sqlserver`, `sqlserver-init` (con
      `depends_on: service_healthy`) y `phpmyadmin` al compose.

**Verificar:** `docker compose up -d` → phpMyAdmin (8081) muestra las 12 tablas de
MariaDB con los mismos datos; `sqlserver-init` termina Exited (0); SSMS/Azure Data
Studio conecta a localhost,11433 y ve la BD; segundo `up -d` no re-ejecuta nada.

## Fase 3 — Las aplicaciones
- [ ] Colocar en `api_generica/` una API CRUD genérica que escuche en el
      puerto 8001 y lea `DB_PROVIDER` + `DB_*` del entorno.
- [ ] Colocar en `api_facturas/` una API CRUD por entidad que escuche en el
      puerto 8002 con las mismas variables.
- [ ] Colocar en `front_flask/` un frontend Flask que escuche en el puerto 8000
      y consuma las APIs vía `API_GENERICA_URL` / `API_FACTURAS_URL`.

> Cada aplicación es un proyecto independiente con su propia especificación;
> para esta infraestructura son cajas negras que cumplen los contratos de
> [6_contracts.md](6_contracts.md).

## Fase 4 — Integración en compose
- [ ] Agregar los servicios `front` (8000), `api-generica` (8001) y `api-facturas`
      (8002) con: build propio, volumen de código + comando con reload,
      `restart: unless-stopped`, y las variables de entorno del plan (§2.1).
- [ ] `DB_PROVIDER: ${DB_PROVIDER:-postgres}` en ambas APIs.
- [ ] Front: `API_GENERICA_URL`/`API_FACTURAS_URL` con hosts internos, y montaje
      extra `.:/workspace:cached`.

**Verificar:** `docker compose up -d --build` → http://localhost:8000 muestra las
dos APIs "en línea"; crear/editar/eliminar un producto desde el front se refleja
en la BD; editar un archivo Python recarga la app sin reconstruir.

## Fase 5 — Cambio de motor
- [ ] Probar los 3 motores: `$env:DB_PROVIDER = "mariadb"; docker compose up -d`
      (y `sqlserver`, y volver a `postgres`).

**Verificar:** el front funciona idéntico con los 3; phpMyAdmin evidencia los
cambios cuando el motor activo es MariaDB.

## Fase 6 — Devcontainer
- [ ] `.devcontainer/devcontainer.json` según plan §4 (service front, workspace
      `/workspace`, extensiones Python + SQLTools, 3 conexiones internas).

**Verificar:** "Dev Containers: Reopen in Container" abre el repo; SQLTools
conecta a los 3 motores; `Ctrl+E Ctrl+E` ejecuta una consulta.

## Fase 7 — Persistencia y reset
- [ ] Validar el ciclo completo de datos.

**Verificar:** insertar registro → `docker compose down` → `up -d` → sigue ahí;
`down -v` → `up -d` → volvió el estado original.

## Fase 8 — Documentación
- [ ] `docs/GUIA_ESTUDIANTE.md` (instalación → primer recorrido → comandos del día a día).
- [ ] `docs/ARQUITECTURA_3_CAPAS.md` y `docs/PRINCIPIOS_SOLID_ACID.md`.
- [ ] Comentarios didácticos en `docker-compose.yml` (diagrama ASCII incluido).
