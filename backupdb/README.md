# backupdb — respaldos de las bases de datos

En esta carpeta se guardan los **respaldos (backups)** de `bdfacturas` en
los **tres motores** del proyecto. Un respaldo captura la BD **tal como
estaba** en ese momento: estructura, datos, triggers y procedimientos.

> ¿En qué se diferencia de los scripts de `db/`? En que esos crean la BD en
> su **estado inicial** (los datos de fábrica del curso), mientras que un
> backup captura **SU estado actual**: lo que usted insertó, editó o borró.
> Si solo quiere volver al estado inicial: `docker compose down -v` y
> volver a subir.

Cada motor tiene su herramienta y su formato — eso también es parte de la
lección (mismo concepto, tres dialectos):

| Motor | Herramienta | Formato |
|---|---|---|
| PostgreSQL | `pg_dump` | `.sql` legible |
| MariaDB | `mariadb-dump` | `.sql` legible |
| SQL Server | `BACKUP DATABASE` (T-SQL) | `.bak` binario propio |

Convención de nombres: `bdfacturas_<motor>_AAAA-MM-DD.sql` / `.bak`.
Todos los comandos se ejecutan desde la **raíz del repositorio**, con el
proyecto corriendo. El patrón es siempre el mismo: **el respaldo se genera
DENTRO del contenedor y luego se copia a esta carpeta** con
`docker compose cp` (así funciona igual en PowerShell, CMD o bash).

---

## PostgreSQL

**Backup:**

```powershell
docker compose exec postgres sh -c "pg_dump -U paradigmas -d bdfacturas_postgres_local --clean --if-exists > /tmp/backup.sql"
docker compose cp postgres:/tmp/backup.sql backupdb/bdfacturas_postgres_2026-08-08.sql
```

(`--clean --if-exists` mete los `DROP ... IF EXISTS`: al restaurar,
reemplaza lo que haya.)

**Restore:**

```powershell
docker compose cp backupdb/bdfacturas_postgres_2026-08-08.sql postgres:/tmp/restore.sql
docker compose exec postgres psql -U paradigmas -d bdfacturas_postgres_local -f /tmp/restore.sql
```

## MariaDB

**Backup:**

```powershell
docker compose exec mariadb sh -c "mariadb-dump -uparadigmas -pparadigmas123 --routines --triggers bdfacturas_mariadb_local > /tmp/backup.sql"
docker compose cp mariadb:/tmp/backup.sql backupdb/bdfacturas_mariadb_2026-08-08.sql
```

(`--routines --triggers`: sin eso el dump no incluye los procedimientos ni
los triggers de facturación.)

**Restore** (el dump trae `DROP TABLE IF EXISTS`, reemplaza lo que haya):

```powershell
docker compose cp backupdb/bdfacturas_mariadb_2026-08-08.sql mariadb:/tmp/restore.sql
docker compose exec mariadb sh -c "mariadb -uroot -pparadigmas123 bdfacturas_mariadb_local < /tmp/restore.sql"
```

> El restore va con **root** a propósito: el dump guarda los triggers con
> su `DEFINER=root`, y MariaDB solo deja recrear objetos "a nombre de otro"
> a un superusuario (con `paradigmas` falla con `ERROR 1227` a mitad del
> restore y los triggers quedan sin crear).

## SQL Server

SQL Server no usa dumps `.sql`: su mecanismo nativo es `BACKUP DATABASE`,
que produce un `.bak` binario (datos + log en un solo archivo).

**Backup:**

```powershell
docker compose exec sqlserver /opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P "Paradigmas123!" -C -Q "BACKUP DATABASE bdfacturas_sqlserver_local TO DISK='/tmp/backup.bak' WITH INIT"
docker compose cp sqlserver:/tmp/backup.bak backupdb/bdfacturas_sqlserver_2026-08-08.bak
```

**Restore** (`WITH REPLACE` pisa la BD actual; `SINGLE_USER` saca las
conexiones abiertas — por ejemplo las de las APIs — durante el restore):

```powershell
docker compose cp backupdb/bdfacturas_sqlserver_2026-08-08.bak sqlserver:/tmp/restore.bak
docker compose exec sqlserver /opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P "Paradigmas123!" -C -Q "ALTER DATABASE bdfacturas_sqlserver_local SET SINGLE_USER WITH ROLLBACK IMMEDIATE; RESTORE DATABASE bdfacturas_sqlserver_local FROM DISK='/tmp/restore.bak' WITH REPLACE; ALTER DATABASE bdfacturas_sqlserver_local SET MULTI_USER;"
```

---

## Para probar el ciclo completo (ejercicio)

1. Haga el backup del motor activo (`DB_PROVIDER`, por defecto postgres).
2. Cambie algo a propósito: cree un producto `PR999` desde el front
   (`http://localhost:8010`) o edite el stock de uno existente.
3. Restaure el backup.
4. `PR999` desapareció (o el stock volvió) — la BD regresó EXACTAMENTE al
   momento del backup. Eso es un respaldo funcionando.

> ⚠️ El restore pisa TODO el contenido actual de la BD con el del archivo.
> Lo que haya cambiado DESPUÉS del backup se pierde. Por eso los respaldos
> se hacen ANTES de operaciones riesgosas (y en producción, con agenda).
