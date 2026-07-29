"""Conexiones a los tres motores de base de datos.

Cada motor se identifica con una clave: postgres | mariadb | sqlserver.
Las URL de conexion llegan por variables de entorno (ver docker-compose.yml).
"""
import os

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

MOTORES = {
    "postgres": os.getenv(
        "POSTGRES_URL",
        "postgresql+psycopg2://paradigmas:paradigmas123@postgres:5432/bdfacturas_postgres_local",
    ),
    "mariadb": os.getenv(
        "MARIADB_URL",
        "mysql+pymysql://paradigmas:paradigmas123@mariadb:3306/bdfacturas_mariadb_local",
    ),
    "sqlserver": os.getenv(
        "SQLSERVER_URL",
        "mssql+pymssql://sa:Paradigmas123!@sqlserver:1433/bdfacturas_sqlserver_local",
    ),
}

_engines: dict[str, Engine] = {}


def get_engine(motor: str) -> Engine:
    """Retorna (y cachea) el engine de SQLAlchemy para el motor indicado."""
    if motor not in MOTORES:
        raise ValueError(f"Motor desconocido: {motor}. Use: {', '.join(MOTORES)}")
    if motor not in _engines:
        _engines[motor] = create_engine(MOTORES[motor], pool_pre_ping=True)
    return _engines[motor]
