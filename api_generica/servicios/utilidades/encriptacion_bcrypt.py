"""Utilidad para hashear y verificar contraseñas con BCrypt."""

import bcrypt

COSTO_POR_DEFECTO: int = 12


def encriptar(valor_original: str, costo: int = COSTO_POR_DEFECTO) -> str:
    """Genera un hash BCrypt de 60 caracteres."""
    if not valor_original or not valor_original.strip():
        raise ValueError("El valor a encriptar no puede estar vacío.")
    if not 4 <= costo <= 31:
        raise ValueError(f"El costo debe estar entre 4 y 31.")

    valor_bytes = valor_original.encode('utf-8')
    salt = bcrypt.gensalt(rounds=costo)
    hash_bytes = bcrypt.hashpw(valor_bytes, salt)
    return hash_bytes.decode('utf-8')


def verificar(valor_original: str, hash_existente: str) -> bool:
    """Compara un texto plano contra un hash BCrypt."""
    if not valor_original or not valor_original.strip():
        raise ValueError("El valor a verificar no puede estar vacío.")
    if not hash_existente or not hash_existente.strip():
        raise ValueError("El hash existente no puede estar vacío.")

    try:
        valor_bytes = valor_original.encode('utf-8')
        hash_bytes = hash_existente.encode('utf-8')
        return bcrypt.checkpw(valor_bytes, hash_bytes)
    except Exception:
        return False
