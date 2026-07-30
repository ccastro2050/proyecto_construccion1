"""
rutas/facturas.py — Consulta de facturas (maestro-detalle).

Aquí NO hay crear/editar: una factura no se arma con un formulario
simple porque toca stock, subtotales y totales (eso lo hacen los
triggers y procedimientos de la base de datos). El objetivo de esta
pantalla es mostrar cómo se consumen DOS recursos relacionados:

    factura              (el "maestro":  numero, fecha, total…)
    productosporfactura  (el "detalle":  qué productos lleva cada una)
"""
from flask import Blueprint, flash, redirect, render_template, session, url_for

from servicios.cliente_api import ClienteApi

bp_facturas = Blueprint("facturas", __name__, url_prefix="/facturas")


def _api() -> ClienteApi:
    """Cliente para la API seleccionada por el usuario."""
    return ClienteApi(session.get("api", "generica"))


@bp_facturas.route("/")
def listar():
    """Lista todas las facturas (el maestro)."""
    exito, resultado = _api().listar("factura")
    if not exito:
        flash(resultado, "danger")
        resultado = []
    return render_template("facturas_lista.html", facturas=resultado)


@bp_facturas.route("/<int:numero>")
def detalle(numero: int):
    """
    Muestra una factura con sus productos.

    Se hacen DOS llamadas a la API:
    1. La factura (maestro)
    2. Todos los productosporfactura, y se filtran en Python los de
       esta factura (compare: en SQL esto sería un WHERE fknumfactura = X)
    """
    api = _api()

    # 1. El maestro
    exito, factura = api.obtener("factura", "numero", numero)
    if not exito:
        flash(factura, "danger")
        return redirect(url_for("facturas.listar"))

    # 2. El detalle: filtrar los renglones de ESTA factura
    exito, todos = api.listar("productosporfactura")
    if not exito:
        flash(todos, "danger")
        todos = []
    detalle_factura = [d for d in todos if d.get("fknumfactura") == numero]

    return render_template(
        "facturas_detalle.html",
        factura=factura,
        detalle=detalle_factura,
    )
