"""
config.py — Configuración centralizada usando pydantic-settings.

Lee variables desde archivos .env según el entorno:
- Production:  solo .env
- Development: .env + .env.development (sobrescribe valores)
"""

import os
from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


# ================================================================
# DETECCIÓN DE ENTORNO
# ================================================================

def get_environment() -> str:
    """Detecta el entorno actual desde la variable ENVIRONMENT."""
    return os.getenv("ENVIRONMENT", "production").lower()


def get_env_file() -> str | tuple[str, str]:
    """
    Retorna qué archivo(s) .env cargar.
    En development carga ambos; en production solo .env.
    """
    env = get_environment()
    if env == "development":
        env_dev = ".env.development"
        if os.path.exists(env_dev):
            return (".env", env_dev)
    return ".env"


# ================================================================
# CONFIGURACIÓN DE BASE DE DATOS
# ================================================================

class DatabaseSettings(BaseSettings):
    """Cadenas de conexión para cada proveedor de base de datos."""

    model_config = SettingsConfigDict(
        env_file=get_env_file(),
        env_file_encoding='utf-8',
        env_prefix='DB_',       # Lee variables que empiezan con DB_
        extra='ignore'
    )

    # Proveedor activo
    provider: str = Field(default='sqlserver')

    # Cadenas de conexión por proveedor
    sqlserver: str = Field(default='')
    sqlserverexpress: str = Field(default='')
    localdb: str = Field(default='')
    postgres: str = Field(default='')
    mysql: str = Field(default='')
    mariadb: str = Field(default='')


# ================================================================
# CONFIGURACIÓN PRINCIPAL
# ================================================================

class Settings(BaseSettings):
    """Agrupa toda la configuración de la aplicación."""

    model_config = SettingsConfigDict(
        env_file=get_env_file(),
        env_file_encoding='utf-8',
        extra='ignore'
    )

    debug: bool = Field(default=False, alias='DEBUG')
    environment: str = Field(default_factory=get_environment)
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)


# ================================================================
# SINGLETON (se crea una sola vez y se reutiliza)
# ================================================================

@lru_cache()
def get_settings() -> Settings:
    """Obtiene la configuración cacheada (singleton)."""
    return Settings()
