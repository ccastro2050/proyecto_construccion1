"""
cliente_api.py — Cliente HTTP que consume las dos APIs.

Esta clase es EL PUENTE entre el front y las APIs. El front nunca
habla con la base de datos: siempre pasa por aquí.

CONCEPTO — ¿Por qué una clase aparte y no requests directo en las rutas?
    1. Un solo lugar donde está la lógica de conexión (si cambia
       una URL o un formato, se corrige aquí y no en 10 archivos).
    2. Las rutas quedan limpias: piden datos y muestran plantillas.
    3. Permite cambiar de API (genérica ↔ facturas) sin tocar las rutas.

CONCEPTO — Diferencia entre las dos APIs (mismas tablas, rutas distintas):
    API Genérica  → hay que decirle la tabla Y la columna clave:
        GET/PUT/DELETE  /api/persona/codigo/P001
    API Facturas  → ya conoce sus entidades y su clave primaria:
        GET/PUT/DELETE  /api/persona/P001
    Las respuestas sí tienen el mismo formato:
        {"tabla": ..., "total": N, "datos": [ {...}, {...} ]}
"""
import requests

import config


class ClienteApi:
    """Consume la API elegida (genérica o facturas) con métodos CRUD."""

    def __init__(self, nombre_api: str):
        """
        nombre_api: "generica" o "facturas".
        Según cuál sea, cambia la URL base y la forma de armar las rutas.
        """
        self.nombre_api = nombre_api
        if nombre_api == "facturas":
            self.url_base = config.API_FACTURAS_URL
        else:
            self.url_base = config.API_GENERICA_URL

    # ------------------------------------------------------------
    # Armado de URLs (aquí está la única diferencia entre las APIs)
    # ------------------------------------------------------------

    def _url_listar(self, tabla: str) -> str:
        """URL para listar todos los registros de una tabla."""
        if self.nombre_api == "facturas":
            return f"{self.url_base}/api/{tabla}/"      # /api/persona/
        return f"{self.url_base}/api/{tabla}"           # /api/persona

    def _url_registro(self, tabla: str, clave: str, valor) -> str:
        """URL para un registro puntual (obtener, actualizar, eliminar)."""
        if self.nombre_api == "facturas":
            # La API de facturas ya sabe cuál es la clave primaria
            return f"{self.url_base}/api/{tabla}/{valor}"
        # La API genérica necesita el NOMBRE de la columna clave
        return f"{self.url_base}/api/{tabla}/{clave}/{valor}"

    # ------------------------------------------------------------
    # Operaciones CRUD
    # Todas retornan una tupla (exito: bool, resultado: datos o mensaje)
    # para que la ruta decida qué mostrar al usuario.
    # ------------------------------------------------------------

    def listar(self, tabla: str) -> tuple[bool, list | str]:
        """READ — Lista los registros de una tabla."""
        try:
            respuesta = requests.get(self._url_listar(tabla), timeout=10)
            if respuesta.status_code == 204:       # 204 = sin contenido (tabla vacía)
                return True, []
            respuesta.raise_for_status()           # lanza excepción si es 4xx/5xx
            return True, respuesta.json().get("datos", [])
        except requests.RequestException as e:
            return False, self._mensaje_error(e)

    def obtener(self, tabla: str, clave: str, valor) -> tuple[bool, dict | str]:
        """READ — Obtiene UN registro por su clave primaria."""
        try:
            respuesta = requests.get(self._url_registro(tabla, clave, valor), timeout=10)
            respuesta.raise_for_status()
            datos = respuesta.json().get("datos", [])
            if not datos:
                return False, f"No existe {tabla} con {clave} = {valor}"
            return True, datos[0]                  # el primer (y único) registro
        except requests.RequestException as e:
            return False, self._mensaje_error(e)

    def crear(self, tabla: str, datos: dict) -> tuple[bool, str]:
        """CREATE — Inserta un registro nuevo. Los datos viajan como JSON."""
        try:
            respuesta = requests.post(self._url_listar(tabla), json=datos, timeout=10)
            respuesta.raise_for_status()
            return True, "Registro creado correctamente."
        except requests.RequestException as e:
            return False, self._mensaje_error(e)

    def actualizar(self, tabla: str, clave: str, valor, datos: dict) -> tuple[bool, str]:
        """UPDATE — Modifica un registro existente."""
        try:
            respuesta = requests.put(self._url_registro(tabla, clave, valor), json=datos, timeout=10)
            respuesta.raise_for_status()
            return True, "Registro actualizado correctamente."
        except requests.RequestException as e:
            return False, self._mensaje_error(e)

    def eliminar(self, tabla: str, clave: str, valor) -> tuple[bool, str]:
        """DELETE — Borra un registro por su clave primaria."""
        try:
            respuesta = requests.delete(self._url_registro(tabla, clave, valor), timeout=10)
            respuesta.raise_for_status()
            return True, "Registro eliminado correctamente."
        except requests.RequestException as e:
            return False, self._mensaje_error(e)

    # ------------------------------------------------------------
    # Diagnóstico
    # ------------------------------------------------------------

    def estado(self) -> dict | None:
        """Consulta la raíz de la API para saber si está viva."""
        try:
            respuesta = requests.get(self.url_base + "/", timeout=5)
            respuesta.raise_for_status()
            return respuesta.json()
        except requests.RequestException:
            return None

    # ------------------------------------------------------------
    # Utilidades internas
    # ------------------------------------------------------------

    @staticmethod
    def _mensaje_error(e: requests.RequestException) -> str:
        """
        Convierte una excepción de requests en un mensaje entendible.
        Si la API respondió con JSON de error, extrae el detalle.
        """
        if e.response is not None:
            try:
                detalle = e.response.json().get("detail", {})
                if isinstance(detalle, dict):
                    return detalle.get("detalle") or detalle.get("mensaje") or str(detalle)
                return str(detalle)
            except ValueError:                     # la respuesta no era JSON
                return f"Error HTTP {e.response.status_code}"
        return f"No se pudo conectar con la API: {e}"
