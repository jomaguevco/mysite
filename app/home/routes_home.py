from flask import Blueprint, render_template, url_for
from app.productos.control_producto import get_featured_products

bp = Blueprint('home', __name__)

@bp.route('/')
@bp.route('/memoriescity.com')
def index():
    featured_products = get_featured_products()
    integrantes = [
        {
            'nombre': 'Yaira Zapata',
            'cargo': 'Fundadora y CEO',
            'email': 'yaizb@memoriescity.com',
            'imagen': 'placeholder-profile.png'
        },
        {
            'nombre': 'Gabriel Gil',
            'cargo': 'Co-Fundador',
            'email': 'gabo@memoriescity.com',
            'imagen': 'placeholder-profile.png'
        },
        {
            'nombre': 'Karelly García',
            'cargo': 'Ingeniera QA',
            'email': 'kare@memoriescity.com',
            'imagen': 'placeholder-profile.png'
        },
        {
            'nombre': 'Luis Delgado',
            'cargo': 'Desarrollador Frontend',
            'email': 'lucho@memoriescity.com',
            'imagen': 'placeholder-profile.png'
        },
        {
            'nombre': 'Mariano Guevara',
            'cargo': 'Diseñador Gráfico',
            'email': 'mariano@memoriescity.com',
            'imagen': 'placeholder-profile.png'
        },
        {
            'nombre': 'Patiño',
            'cargo': '',
            'email': 'maria@memoriescity.com',
            'imagen': 'placeholder-profile.png'
        }
    ]

    return render_template('index.html', featured_products=featured_products, integrantes=integrantes)

@bp.route('/blog')
def blog():
    return render_template('blog.html')

@bp.route('/acercade')
def acercade():
    return render_template('acercade.html')

@bp.route('/contacto')
def contacto():
    return render_template('contacto.html')

@bp.route('/tienda')
def tienda():
    return render_template('tienda.html')

@bp.route('/privacidad')
def privacidad():
    return render_template('politica_privacidad.html')