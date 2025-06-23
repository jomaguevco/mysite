from flask import Blueprint

bp = Blueprint('descuento', __name__)

from . import routes_descuento