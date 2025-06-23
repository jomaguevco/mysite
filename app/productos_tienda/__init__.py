from flask import Blueprint

bp = Blueprint('productos_tienda', __name__)

from . import routes_productos_tienda