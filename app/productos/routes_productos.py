from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from flask_login import current_user, login_required
from .control_producto import get_product_details, get_related_products, get_products, obtener_todos_los_productos, buscar_por_nombre, buscar_generos, get_products_by_filters
from .forms_producto import ReviewForm
from ..cart.forms_carrito import AddToCartForm
from app.bd import get_db_connection
from .control_producto import get_products_by_type
from app.auth.decoradores_jwt import jwt_login_required
import requests

from app import csrf

bp = Blueprint('productos', __name__, url_prefix='/productos')

@csrf.exempt
def dict_fetchall(cursor):
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]

def fetch_deezer_album_info(album_id):
    url = f"https://api.deezer.com/album/{album_id}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return {}

@csrf.exempt
@bp.route('/<int:product_id>')
def product_detail(product_id):
    product = get_product_details(product_id)
    if not product:
        flash('Producto no encontrado', 'error')
        return redirect(url_for('tienda.index'))

    # Agregar la clave 'max_selectable'
    product['max_selectable'] = min(10, product.get('STOCK', 0))

    related_products = get_related_products(product['ID_GENERO'], product_id)
    form = ReviewForm()

    deezer_album_info = {}
    if product['id_deezer']:
        print(f"El id del deezer es: {product['id_deezer']}")
        deezer_album_info = fetch_deezer_album_info(product['id_deezer'])
    else:
        print(f"No se encontró album de deezer")

    # Renderizar la vista con la información del producto y del álbum
    return render_template(
        'productos/product_detail.html',
        product=product,
        related_products=related_products,
        deezer_album_info=deezer_album_info,
        form=form
    )



@csrf.exempt
@bp.route('/cart')
def cart():
    cart = session.get('cart', [])
    total = sum(float(item['subtotal']) for item in cart)  # Convertimos cada subtotal a float
    return render_template('carrito.html', cart=cart, total=total)

@csrf.exempt
@bp.route('/<int:product_id>/review', methods=['POST'])
@jwt_login_required
def add_review(product_id):
    form = ReviewForm()
    if form.validate_on_submit():
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                sql = """
                INSERT INTO RESENA (ID_PRODUCTO, ID_USUARIO, PUNTUACION, COMENTARIO, FECHA_RESENA, ESTADO)
                VALUES (%s, %s, %s, %s, CURDATE(), 'A')
                """
                cursor.execute(sql, (product_id, current_user.get_id(), form.rating.data, form.comment.data))
            conn.commit()
            flash('Reseña añadida con éxito', 'success')
        except Exception as e:
            conn.rollback()
            flash('Error al añadir la reseña', 'error')
        finally:
            conn.close()
    else:
        flash('Error en el formulario de reseña', 'error')
    return redirect(url_for('productos.product_detail', product_id=product_id))


@csrf.exempt
@bp.route('/vinilos')
def vinilos():
    page = request.args.get('page', 1, type=int)
    genero_id = request.args.get('filtro_genero')
    precio_max_str = request.args.get('filtro_precio', '500')

    try:
        precio_max = int(precio_max_str)
    except ValueError:
        precio_max = 500

    descuento = request.args.get('filtro_descuento')

    print(f"Filtros: genero_id={genero_id}, precio_max={precio_max}, descuento={descuento}")
    products = get_products_by_filters(1, page, genero_id, precio_max, descuento)

    # Calcula el máximo permitido para el select y añade al contexto
    for product in products:
        product['max_selectable'] = min(10, product['STOCK'])

    generos = buscar_generos()

    return render_template('productos/list.html', products=products, generos=generos, product_type='Vinilos')



@csrf.exempt
@bp.route('/cds')
def cds():
    page = request.args.get('page', 1, type=int)
    genero_id = request.args.get('filtro_genero')
    precio_max_str = request.args.get('filtro_precio', '500')

    try:
        precio_max = int(precio_max_str)
    except ValueError:
        precio_max = 500

    descuento = request.args.get('filtro_descuento')

    print(f"Filtros: genero_id={genero_id}, precio_max={precio_max}, descuento={descuento}")
    products = get_products_by_filters(2, page, genero_id, precio_max, descuento)

    # Calcula el máximo permitido para el select y añade al contexto
    for product in products:
        product['max_selectable'] = min(10, product['STOCK'])

    generos = buscar_generos()

    return render_template('productos/list.html', products=products, generos=generos, product_type='CDs')



@csrf.exempt
@bp.route('/cassettes')
def cassettes():
    page = request.args.get('page', 1, type=int)
    genero_id = request.args.get('filtro_genero')
    precio_max_str = request.args.get('filtro_precio', '500')

    try:
        precio_max = int(precio_max_str)
    except ValueError:
        precio_max = 500

    descuento = request.args.get('filtro_descuento')

    print(f"Filtros: genero_id={genero_id}, precio_max={precio_max}, descuento={descuento}")
    products = get_products_by_filters(3, page, genero_id, precio_max, descuento)

    # Calcula el máximo permitido para el select y añade al contexto
    for product in products:
        product['max_selectable'] = min(10, product['STOCK'])

    generos = buscar_generos()

    return render_template('productos/list.html', products=products, generos=generos, product_type='Cassettes')



@csrf.exempt
@bp.route('/todos')
def todos():
    genero_id = request.args.get('filtro_genero')  # Obtener el filtro de género

    # Obtener productos filtrados por género
    print(f"Filtro de género: {genero_id}")
    products = obtener_todos_los_productos(genero_id)
    generos = buscar_generos()

    return render_template('productos/list.html', products=products, generos=generos, product_type='Todos los productos')


@csrf.exempt
@bp.route('/tienda', methods=['GET'])
def tienda():
    genero_id = request.args.get('filtro_genero')  # Obtén el valor del género desde el request.GET

    # Usar la función que filtra productos por género
    productos = obtener_todos_los_productos(genero_id)

    # Agrega la clave 'max_selectable' a cada producto
    for producto in productos:
        producto['max_selectable'] = min(10, producto.get('STOCK', 0))  # Máximo entre 10 y el stock disponible

    generos = buscar_generos()  # Recupera todos los géneros

    return render_template('tienda.html', productos=productos, generos=generos)



@csrf.exempt
@bp.route('/busqueda', methods=['GET'])
def busqueda():
    # Obtener el valor de búsqueda desde los parámetros de la URL (GET request)
    nombre_producto = request.args.get('nombre_producto', '').strip()

    print(f"Nombre de producto: {nombre_producto}")

    # Llama a la función de búsqueda solo si se ha proporcionado un nombre de producto
    if nombre_producto:
        productos = buscar_por_nombre(nombre_producto)
    else:
        productos = []  # Devuelve una lista vacía si no hay nombre de producto

    return render_template('productos_busqueda.html', productos=productos)
