"""
app.py — Punto de entrada del frontend Flask.

Este archivo hace 3 cosas:
1. Crea la aplicación Flask.
2. Registra los "blueprints" (grupos de rutas: inicio, productos, …).
3. Deja disponible en todas las plantillas cuál API está activa.

CONCEPTO — ¿Qué es un blueprint?
    Es la forma de Flask de partir la aplicación en módulos.
    En vez de tener 20 rutas en un solo archivo gigante, cada
    tema (productos, personas, facturas) vive en su propio archivo
    dentro de la carpeta rutas/.

CONCEPTO — ¿Qué es la sesión (session)?
    Un pequeño espacio de memoria POR USUARIO que viaja en una
    cookie firmada. Aquí la usamos para recordar qué API eligió
    el usuario (genérica o facturas) entre una página y otra.

Ejecución (la hace docker-compose automáticamente):
    flask --app app run --host 0.0.0.0 --port 5000 --debug
"""
from flask import Flask, redirect, request, session, url_for

import config
from rutas.inicio import bp_inicio
from rutas.productos import bp_productos
from rutas.personas import bp_personas
from rutas.facturas import bp_facturas
from rutas.explorador import bp_explorador

# ================================================================
# CREAR LA APLICACIÓN
# ================================================================
app = Flask(__name__)
app.secret_key = config.SECRET_KEY     # necesaria para usar session y flash

# ================================================================
# REGISTRAR LOS BLUEPRINTS (grupos de rutas)
# ================================================================
app.register_blueprint(bp_inicio)          # /
app.register_blueprint(bp_productos)       # /productos…
app.register_blueprint(bp_personas)        # /personas…
app.register_blueprint(bp_facturas)        # /facturas…
app.register_blueprint(bp_explorador)      # /explorador…


# ================================================================
# API ACTIVA — disponible en todas las plantillas
# ================================================================

@app.context_processor
def inyectar_api_activa():
    """
    Un context_processor agrega variables a TODAS las plantillas.
    Así base.html siempre sabe qué API está seleccionada sin que
    cada ruta tenga que pasarla a mano.
    """
    return {"api_activa": session.get("api", "generica")}


@app.route("/cambiar-api/<nombre>")
def cambiar_api(nombre: str):
    """
    Cambia la API activa (generica ↔ facturas) y vuelve a la página
    donde estaba el usuario. Se llama desde el selector del menú.
    """
    if nombre in ("generica", "facturas"):
        session["api"] = nombre
    # request.referrer = la página desde donde se hizo clic
    return redirect(request.referrer or url_for("inicio.pagina_inicio"))
