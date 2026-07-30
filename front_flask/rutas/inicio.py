"""
rutas/inicio.py — Página de inicio del frontend.

Muestra el estado de las dos APIs y explica la arquitectura.
Es el ejemplo más simple de una ruta Flask:
    1. Recibe la petición del navegador
    2. Pide datos (aquí: el estado de cada API)
    3. Renderiza una plantilla HTML con esos datos
"""
from flask import Blueprint, render_template

from servicios.cliente_api import ClienteApi

# El blueprint agrupa las rutas de este archivo.
# "inicio" es su nombre interno (se usa en url_for("inicio.pagina_inicio")).
bp_inicio = Blueprint("inicio", __name__)


@bp_inicio.route("/")
def pagina_inicio():
    """Página principal: estado de las 2 APIs."""
    # Se consulta el endpoint raíz de cada API para saber si responden
    estado_generica = ClienteApi("generica").estado()
    estado_facturas = ClienteApi("facturas").estado()

    # render_template busca el archivo en la carpeta templates/
    # y le pasa las variables para que la plantilla las muestre
    return render_template(
        "inicio.html",
        estado_generica=estado_generica,
        estado_facturas=estado_facturas,
    )
