from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
import pymysql
from datetime import date, timedelta, datetime
import random
import string
from app import csrf
from flask_login import current_user
from decimal import Decimal
from .control_carrito import (
    obtener_detalles_producto, agregar_producto_a_carrito, vaciar_carrito, actualizar_cantidad_carrito, eliminar_producto_carrito,
    verificar_producto_carrito, obtener_items_carrito, obtener_carrito_checkout, insertar_tarjeta, procesar_venta, obtener_carritos,
    obtener_carrito_usuario
)

from flask_jwt_extended import jwt_required, get_jwt_identity

bp = Blueprint('carrito', __name__, url_prefix='/carrito')

# Añadir producto al carrito
@csrf.exempt
@bp.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    #Verifica si el usuario está autenticado
    if not current_user.is_authenticated:
        flash('Por favor, inicie sesión para agregar productos al carrito.', 'warning')
        return redirect(url_for('auth.login'))

    # Obtener datos del formulario
    product_id = int(request.form['product_id'])
    tipo_producto_id = int(request.form['tipo_producto_id'])
    cantidad = int(request.form['cantidad'])
    usuario_id = current_user.id

    try:
        # Obtener detalles del producto
        producto = obtener_detalles_producto(product_id, tipo_producto_id)

        if producto is None:
            flash("Producto no encontrado.", 'error')
            return redirect(url_for('carrito.cart'))

        #Verifica si hay suficiente stock del producto
        if cantidad > producto['STOCK']:
            flash(f"No hay suficiente stock para {producto['NOMBRE_PRODUCTO']}. Solo quedan {producto['STOCK']} unidades.", 'error')
            return redirect(url_for('carrito.product', product_id=product_id))

        # Calcular monto con descuento e impuesto
        descuento = producto['DESCUENTO']
        precio_con_descuento = producto['PRECIO_CON_DESCUENTO']
        monto = precio_con_descuento * cantidad * Decimal(1.18)

        # Agregar producto al carrito
        if agregar_producto_a_carrito(usuario_id, tipo_producto_id, product_id, cantidad, precio_con_descuento, monto):
            flash(f"{cantidad} {producto['NOMBRE_PRODUCTO']} agregado(s) al carrito.", 'success')
        else:
            flash("Error al agregar el producto al carrito.", 'error')

    except Exception as e:
        flash(f"Error al procesar el carrito: {str(e)}", 'error')

    return redirect(url_for('carrito.cart'))

@csrf.exempt
@bp.route('/update_quantity/<int:product_id>/<int:tipo_producto_id>', methods=['POST'])
def update_quantity(product_id, tipo_producto_id):
    if not current_user.is_authenticated:
        flash('Por favor, inicie sesión para modificar el carrito.', 'warning')
        return redirect(url_for('auth.login'))

    new_quantity = request.form.get('quantity')
    usuario_id = current_user.id

    try:
        carrito_item = verificar_producto_carrito(usuario_id, product_id, tipo_producto_id)
        if not carrito_item:
            flash('Producto no encontrado en el carrito.', 'error')
            return redirect(url_for('carrito.cart'))

        nueva_cantidad = int(new_quantity)
        if nueva_cantidad < 1 or nueva_cantidad > 10:
            flash('Cantidad no válida. Seleccione entre 1 y 10.', 'error')
            return redirect(url_for('carrito.cart'))

        actualizar_cantidad_carrito(carrito_item['ID_CARRITO'], nueva_cantidad)

    except ValueError:
        flash('Por favor, seleccione un número válido.', 'error')
    except Exception as e:
        flash(f'Error al actualizar la cantidad: {str(e)}', 'error')

    return redirect(url_for('carrito.cart'))

@csrf.exempt
@bp.route('/remove_from_cart/<int:product_id>/<int:tipo_producto_id>', methods=['POST'])
def remove_from_cart(product_id, tipo_producto_id):
    usuario_id = current_user.id
    try:
        eliminar_producto_carrito(usuario_id, product_id, tipo_producto_id)
    except Exception as e:
        flash(f"Error al eliminar el producto del carrito: {str(e)}", 'error')

    return redirect(url_for('carrito.cart'))

@csrf.exempt
@bp.route('/reset_cart', methods=['POST'])
def reset_cart():
    usuario_id = current_user.id
    try:
        vaciar_carrito(usuario_id)
    except Exception as e:
        flash(f"Error al vaciar el carrito: {str(e)}", 'error')

    return redirect(url_for('carrito.cart'))

@csrf.exempt
@bp.route('/cart', methods=['GET'])
def cart():
    usuario_id = current_user.id
    try:
        cart, total = obtener_items_carrito(usuario_id)
    except Exception as e:
        flash(f"Error al obtener los productos del carrito: {str(e)}", 'error')
        cart, total = [], 0

    return render_template('carrito.html', cart=cart, total=total)



@csrf.exempt
@bp.route('/checkout', methods=['GET', 'POST'])
def checkout():
    usuario_id = current_user.id

    # Manejo del método GET para mostrar el carrito en el checkout
    if request.method == 'GET':
        try:
            cart_pantalla, monto_pantalla = obtener_carrito_checkout(usuario_id)
            monto_env = monto_pantalla + 10
            return render_template('checkout.html', cart=cart_pantalla, monto=monto_pantalla, monto_env=monto_env)
        except Exception as e:
            flash(f"Error al obtener los productos del carrito: {str(e)}", 'error')
            return redirect(url_for('carrito.cart'))

    # Manejo del método POST para procesar la compra
    elif request.method == 'POST':
        try:
            # Datos del formulario
            direccion = request.form.get('direccion')
            ciudad = request.form.get('ciudad')
            provincia = request.form.get('provincia')

            tipo_tarjeta = request.form.get('tipo_tarjeta')
            numero_tarjeta = request.form.get('numero_tarjeta')
            fecha_vencimiento = request.form.get('fecha_vencimiento')
            cvv = request.form.get('cvv')

            # Validar y procesar fecha de vencimiento
            if fecha_vencimiento:
                print("Fecha no válida")
            else:
                return redirect(url_for('carrito.checkout'))

            # Insertar tarjeta y obtener su ID
            tarjeta_id = insertar_tarjeta(usuario_id, tipo_tarjeta, numero_tarjeta, fecha_vencimiento, cvv)

            print("Check point: Cart pantalla")

            # Obtener carrito y procesar venta
            cart_pantalla, monto_pantalla = obtener_carrito_checkout(usuario_id)

            print("Tipo de cart_pantalla:", type(cart_pantalla))
            print(cart_pantalla)
            print("Tipo de monto_pantalla:", type(monto_pantalla))
            print(monto_pantalla)

            total_con_envio = monto_pantalla + 10
            procesar_venta(usuario_id, tarjeta_id, monto_pantalla, total_con_envio, cart_pantalla, direccion, provincia, ciudad)
            print("Se procesa la venta")


            # --- NUEVO: Emitir notificación y guardarla ---
            # from app import socketio
            # from app.notificacion.control_notificacion import insertar_notificacion

            # items_str = ", ".join([f'{item["CANTIDAD"]}x "{item["NOMBRE_PRODUCTO"]}"' for item in cart_pantalla])
            # mensaje = f"♪ Compra realizada por {current_user.nombre_usuario}: {items_str} | Total: S/. {total_con_envio:.2f}"

            # socketio.emit('nueva_venta', {'mensaje': mensaje})
            # insertar_notificacion(mensaje)
# ----------------------------------------------



            # Generar número de seguimiento para el envío
            numero_seguimiento = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
            fecha_entrega = date.today() + timedelta(days=5)  # Fecha estimada de entrega
            vaciar_carrito(usuario_id)
            # Redirigir a la página de confirmación
            return redirect(url_for('carrito.checkout_info', monto_env=total_con_envio, numero_seguimiento=numero_seguimiento, fecha_entrega=fecha_entrega))
        except Exception as e:
            flash(f"Error al procesar el checkout: {str(e)}", 'error')
            return redirect(url_for('carrito.checkout'))


@csrf.exempt
@bp.route('/checkout_info')
def checkout_info():
    # Obtener el monto y número de seguimiento desde los parámetros de la URL

    usuario_id = current_user.id

    total = request.args.get('monto_env', type=float)
    numero_seguimiento = request.args.get('numero_seguimiento')
    fecha_entrega = request.args.get('fecha_entrega')

    # Comprobar si los valores existen
    if total is None or numero_seguimiento is None:
        print('Faltan datos de la transacción.')
        flash('Hubo un problema al procesar su pedido. Intente nuevamente.', 'error')
        return redirect(url_for('carrito.cart'))  # Redirigir al carrito si faltan datos

    # Imprimir valores para depuración
    print(f"El total sería {total}")
    print(f"Numero de seguimiento: {numero_seguimiento}")
    print(f"Fecha de envío: {fecha_entrega}")

    # Renderizar la página de confirmación con los detalles, modificar la fecha de entrega
    return render_template('checkout_info.html', total=total, numero_seguimiento=numero_seguimiento, fecha_entrega=fecha_entrega)

##APIS CARRITO
@csrf.exempt
@bp.route('/api_mostrar_carritos', methods=['GET'])
@jwt_required()
def api_mostrar_carritos():
    """Endpoint para obtener todos los carritos"""
    if current_user.is_authenticated and current_user.id_rol != 1:
        return jsonify({
            "data": [],
            "message": "No tienes permiso para acceder a esta información",
            "status": 0
        }), 403

    carritos = obtener_carritos()
    carritos_serializados = [
        {
            "id_carrito": carrito["ID_CARRITO"],
            "nombre_usuario": carrito["NOMBRE_USUARIO"],
            "nonbre_producto": carrito["NOMBRE_PRODUCTO"],
            "cantidad": carrito["CANTIDAD"],
            "precio": carrito["PRECIO"],
            "monto_total": carrito["MONTO"]
        }
        for carrito in carritos
    ]

    return jsonify({
        "data": carritos_serializados,
        "message": "Carritos obtenidos correctamente",
        "status": 1
    }), 200


@csrf.exempt
@bp.route('/api_mostrar_carrito_usuario', methods=['POST'])
@jwt_required()
def api_mostrar_carrito_usuario():
    """Endpoint para obtener el carrito de un usuario"""
    if current_user.is_authenticated and current_user.id_rol != 1:
        return jsonify({
            "data": [],
            "message": "No tienes permiso para acceder a esta información",
            "status": 0
        }), 403

    data = request.get_json()
    if not data:
        return jsonify({
            "data": [],
            "message": "Faltan datos",
            "status": 0
        }), 400

    id_usuario = data['id_usuario']

    carritos = obtener_carrito_usuario(id_usuario)
    carritos_serializados = [
        {
            "id_carrito": carrito["ID_CARRITO"],
            "nombre_usuario": carrito["NOMBRE_USUARIO"],
            "nonbre_producto": carrito["NOMBRE_PRODUCTO"],
            "cantidad": carrito["CANTIDAD"],
            "precio": carrito["PRECIO"],
            "monto_total": carrito["MONTO"]
        }
        for carrito in carritos
    ]

    return jsonify({
        "data": carritos_serializados,
        "message": "Carritos obtenidos correctamente",
        "status": 1
    }), 200


@csrf.exempt
@bp.route('/api_agregar_carrito', methods=['POST'])
@jwt_required()
def api_agregar_carrito():
    if current_user.is_authenticated and current_user.id_rol != 1:
        return jsonify({
            "data": [],
            "message": "No tienes permiso para acceder a esta información",
            "status": 0
        }), 403

    data = request.get_json()
    if not data:
        return jsonify({
            "data": [],
            "message": "Faltan datos",
            "status": 0
        }), 400

    id_usuario = data['id_usuario']
    id_tipo_producto = data['id_tipo_producto']
    id_producto = data['id_producto']
    cantidad = data['cantidad']
    precio_con_descuento = data['precio']
    monto = precio_con_descuento * cantidad

    agregar_producto_a_carrito(id_usuario, id_tipo_producto, id_producto, cantidad, precio_con_descuento, monto)
    return jsonify({
        "data": [],
        "message": "Producto agregado al carrito",
        "status": 1
    }), 200


@csrf.exempt
@bp.route('/api_eliminar_carrito', methods=['POST'])
@jwt_required()
def api_eliminar_carrito():
    if current_user.is_authenticated and current_user.id_rol != 1:
        return jsonify({
            "data": [],
            "message": "No tienes permiso para acceder a esta información",
            "status": 0
        }), 403

    data = request.get_json()
    if not data:
        return jsonify({
            "data": [],
            "message": "Faltan datos",
            "status": 0
        }), 400

    id_usuario = data['id_usuario']
    id_producto = data['id_producto']
    id_tipo_producto = data['id_tipo_producto']

    eliminar_producto_carrito(id_usuario, id_producto, id_tipo_producto)
    return jsonify({
        "data": [],
        "message": "Producto eliminado del carrito",
        "status": 1
    }), 200

@csrf.exempt
@bp.route('/api_vaciar_carrito', methods=['POST'])
@jwt_required()
def api_vaciar_carrito():
    if current_user.is_authenticated and current_user.id_rol != 1:
        return jsonify({
            "data": [],
            "message": "No tienes permiso para acceder a esta información",
            "status": 0
        }), 403

    data = request.get_json()
    if not data:
        return jsonify({
            "data": [],
            "message": "Faltan datos",
            "status": 0
        }), 400

    id_usuario = data['id_usuario']

    vaciar_carrito(id_usuario)
    return jsonify({
        "data": [],
        "message": "Carrito vaciado correctamente",
        "status": 1
    }), 200


@csrf.exempt
@bp.route('/api_modificar_cantidad_producto', methods=['POST'])
@jwt_required()
def api_modificar_cantidad_producto():
    if current_user.is_authenticated and current_user.id_rol != 1:
        return jsonify({
            "data": [],
            "message": "No tienes permiso para acceder a esta información",
            "status": 0
        }), 403

    data = request.get_json()
    if not data:
        return jsonify({
            "data": [],
            "message": "Faltan datos",
            "status": 0
        }), 400

    id_carrito = data.get('id_carrito')
    cantidad = data.get('nueva_cantidad')

    # Verificar si los datos requeridos están presentes
    if id_carrito is None or cantidad is None:
        return jsonify({
            "data": [],
            "message": "ID del carrito o cantidad faltante",
            "status": 0
        }), 400

    # Validar que la cantidad no sea negativa
    if cantidad < 0:
        return jsonify({
            "data": [],
            "message": "La cantidad no puede ser negativa",
            "status": 0
        }), 400

    try:
        # Actualizar cantidad en el carrito
        actualizar_cantidad_carrito(id_carrito, cantidad)
        return jsonify({
            "data": [],
            "message": "Carrito actualizado correctamente",
            "status": 1
        }), 200
    except Exception as e:
        # Manejar posibles errores en la operación de actualización
        return jsonify({
            "data": [],
            "message": f"Error al actualizar el carrito: {str(e)}",
            "status": 0
        }), 500
