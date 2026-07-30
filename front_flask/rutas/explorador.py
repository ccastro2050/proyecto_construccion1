"""
rutas/explorador.py — Explorador de cualquier tabla.

Demuestra el poder de la API genérica: un solo endpoint
(/api/{tabla}) sirve para consultar CUALQUIER tabla de la base
de datos, sin que nadie haya programado esa tabla en la API.

El listado de columnas se deduce de los propios datos: las
claves del primer registro son los nombres de las columnas.
"""
from flask import Blueprint, flash, render_template, request, session

from servicios.cliente_api import ClienteApi

bp_explorador = Blueprint("explorador", __name__, url_prefix="/explorador")

# Las 12 tablas de bdfacturas (para armar el menú desplegable)
TABLAS = [
    "empresa", "persona", "producto", "cliente", "vendedor",
    "factura", "productosporfactura", "usuario", "rol",
    "rol_usuario", "ruta", "rutarol",
]


@bp_explorador.route("/")
def explorar():
    """Muestra el contenido de la tabla elegida en el menú."""
    # request.args trae los parámetros de la URL: /explorador/?tabla=persona
    tabla = request.args.get("tabla", "persona")

    api = ClienteApi(session.get("api", "generica"))
    exito, filas = api.listar(tabla)
    if not exito:
        flash(filas, "danger")
        filas = []

    # Las columnas se deducen del primer registro recibido
    columnas = list(filas[0].keys()) if filas else []

    return render_template(
        "explorador.html",
        tablas=TABLAS,
        tabla_actual=tabla,
        columnas=columnas,
        filas=filas,
    )
