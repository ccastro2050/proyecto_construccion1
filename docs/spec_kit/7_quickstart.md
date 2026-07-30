# Quickstart — Proyecto completo

> **Documento 7 de 8** del spec kit raíz. Validación del sistema ya construido.
> (La guía paso a paso para estudiantes es `docs/GUIA_ESTUDIANTE.md`; esto es la
> versión condensada de verificación.)

---

## 1. Levantar

```powershell
git clone https://github.com/ccastro2050/proyecto_construccion1.git
cd proyecto_construccion1
docker compose up -d --build     # primera vez: varios minutos
```

## 2. Verificación en 10 pasos

```powershell
docker compose ps
# Esperado: front, api-generica, api-facturas, postgres, mariadb, sqlserver,
# phpmyadmin corriendo; sqlserver-init con Exited (0)
```

1. **http://localhost:8000** → las dos APIs con badge verde "en línea"
   (SQL Server puede tardar 1–2 min).
2. **Productos** → crear/editar/eliminar un producto (CRUD completo con flashes).
3. Cambiar la **API activa** (Genérica ↔ Facturas) y repetir el paso 2: idéntico.
4. **Explorador** → recorrer las 12 tablas.
5. **http://localhost:8001/swagger** y **http://localhost:8002/docs** abren.
6. **http://localhost:8081** (phpMyAdmin) entra directo y muestra
   `bdfacturas_mariadb_local`.
7. Cambio de motor:
   ```powershell
   $env:DB_PROVIDER = "mariadb"; docker compose up -d
   ```
   → el front sigue igual; lo creado ahora se ve en phpMyAdmin. Volver:
   `$env:DB_PROVIDER = "postgres"; docker compose up -d`.
8. Persistencia: insertar un registro → `docker compose down` → `up -d` →
   sigue ahí.
9. Reset: `docker compose down -v` → `up -d` → datos originales de vuelta.
10. Herramienta externa: pgAdmin a `localhost:15432` /
    `paradigmas`/`paradigmas123` ve las 12 tablas (o HeidiSQL 13306 / SSMS 11433).

Opcional: `F1 → Dev Containers: Reopen in Container` → SQLTools con las 3
conexiones listas.

## 3. Problemas frecuentes

| Síntoma | Diagnóstico |
|---|---|
| Badge rojo en una API | `docker compose logs api-generica` (o api-facturas) |
| SQL Server nunca sano | Necesita ~2 GB RAM; trabajar con postgres/mariadb |
| localhost:8000 no abre | `docker compose ps` + `docker compose logs front` |
| Puerto ocupado (8000/8081/…) | Cerrar el otro programa o cambiar el mapeo en compose |
| Cambié un init.sql y no pasa nada | Solo corren con volumen vacío: `down -v` + `up -d` |
| Todo roto | `docker compose down -v` + `docker compose up -d --build` |
