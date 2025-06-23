from flask import Blueprint

bp = Blueprint('tienda', __name__)

from . import routes_tienda