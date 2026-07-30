#!/bin/bash
# ==============================================================
# Inicializador de SQL Server para Proyecto Construcción 1.
# Crea la base de datos bdfacturas_sqlserver_local y ejecuta el
# script SOLO la primera vez (si la BD no existe todavia).
# ==============================================================
set -e

SQLCMD=/opt/mssql-tools18/bin/sqlcmd
SERVER=sqlserver
DB=bdfacturas_sqlserver_local

echo "[init] Verificando si la base de datos $DB existe..."
EXISTE=$($SQLCMD -S $SERVER -U sa -P "$MSSQL_SA_PASSWORD" -C -h -1 -W -Q "SET NOCOUNT ON; SELECT COUNT(*) FROM sys.databases WHERE name = '$DB'")

if [ "$EXISTE" = "1" ]; then
    echo "[init] La base de datos $DB ya existe. No se hace nada."
    exit 0
fi

echo "[init] Creando base de datos $DB..."
$SQLCMD -S $SERVER -U sa -P "$MSSQL_SA_PASSWORD" -C -Q "CREATE DATABASE $DB"

echo "[init] Ejecutando script bdfacturas.sql..."
$SQLCMD -S $SERVER -U sa -P "$MSSQL_SA_PASSWORD" -C -d $DB -i /scripts/bdfacturas.sql

echo "[init] SQL Server inicializado correctamente."
