from flask import Blueprint, render_template, request
from .control_tienda import get_products, get_genres
from .forms_tienda import FilterForm

bp = Blueprint('tienda', __name__)

@bp.route('/')
def index():
    form = FilterForm(request.args)
    products = get_products(form.data if form.validate() else None)
    genres = get_genres()
    return render_template('tienda.html', products=products, genres=genres, form=form)