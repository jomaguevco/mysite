from flask import Blueprint

bp = Blueprint('perfil', __name__)

from . import routes_perfil