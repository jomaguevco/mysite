from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from werkzeug.utils import secure_filename
from .control_productos_tienda import (
    obtener_productos, dar_de_baja_producto, obtener_producto_por_id,
    actualizar_producto, existe_producto, insertar_producto,
    obtener_tipos_producto, obtener_generos, obtener_descuentos,
    insertar_o_actualizar_detalle_tipo_producto, eliminar_detalle_tipo_producto, insertar_detalle_tipo_producto2, obtener_productos2, obtener_tipos_producto2,obtener_producto_por_nombre1,
    obtener_detalle_producto, actualizar_detalle_tipo_producto, verificar_asociacion_detalle_venta,mostrar_productos, listarProductos, obtener_productos_por_id, validar_producto_sin_asociaciones,eliminar_producto,
    obtener_detalle_tipo_producto

)
import os
from datetime import datetime
from app import csrf
from flask_jwt_extended import jwt_required, get_jwt_identity

bp = Blueprint('producto', __name__, url_prefix='/productos_tienda')

@csrf.exempt
@bp.route('/panel_producto_home', methods=['GET'])
def panel_producto_home():
    nombre_producto = request.args.get('nombre_producto')
    filtro_genero = request.args.get('filtro_genero')

    # Obtener productos con los filtros aplicados
    productos = obtener_productos(nombre_producto, filtro_genero)
    generos = obtener_generos()  # Asegúrate de que esta función también obtenga los géneros

    return render_template('panel/producto.html', productos=productos, generos=generos)



@csrf.exempt
@bp.route('/insertar_detalle_tipo_producto', methods=['GET', 'POST'])
def insertar_detalle_tipo_producto():
    if request.method == 'POST':

        form_data = request.form
        id_producto = form_data.get('id_producto')
        id_tipo_producto = form_data.get('id_tipo_producto')
        stock = form_data.get('stock')
        precio = form_data.get('precio')


        imagen = request.files['imagen']
        filename = secure_filename(imagen.filename)
        upload_folder = '/home/grupo004/mysite/app/static/media'

        upload_path = os.path.join(upload_folder, filename)
        imagen.save(upload_path)

        # Insertar detalle en la base de datos
        if insertar_detalle_tipo_producto2(id_tipo_producto, id_producto, stock, precio, filename):
            return redirect(url_for('producto.panel_producto_home'))


    id_producto = request.args.get('id_producto', None)
    tipos = obtener_tipos_producto2()


    producto = obtener_producto_por_id(id_producto)


    return render_template('panel/agregar_nuevo_producto.html', producto=producto, tipos=tipos)




@csrf.exempt
@bp.route("/formulario_agregar_producto")
def formulario_agregar_producto():
    generos = obtener_generos()
    descuentos = obtener_descuentos()
    tipos_producto = obtener_tipos_producto()
    return render_template("panel/agregar_producto.html", generos=generos, descuentos=descuentos, tipos_producto=tipos_producto)


@csrf.exempt
@bp.route("/asignar_detalle_producto", methods=['GET', 'POST'])
def asignar_detalle_producto():
    if request.method == 'POST':
        # Recoger datos del formulario
        form_data = request.form
        id_producto = form_data.get('id_producto')
        id_tipo_producto = form_data.get('id_tipo_producto')
        stock = form_data.get('stock')
        precio = form_data.get('precio')

        # Obtener la imagen
        imagen = request.files['imagen']
        filename = secure_filename(imagen.filename)

        # Construir la ruta completa para guardar la imagen
        upload_path = os.path.join(os.getcwd(), 'mysite', 'app', 'static', 'media', filename)

        # Guardar la imagen en la carpeta de subida
        imagen.save(upload_path)

        # Llamar a la función para insertar el detalle en la base de datos
        if insertar_detalle_tipo_producto2(id_tipo_producto, id_producto, stock, precio, filename):
            flash('Detalle de tipo de producto insertado exitosamente', 'success')
            return redirect(url_for('producto.panel_producto_home'))
        else:
            flash('Error al insertar el detalle de producto', 'error')

    # Obtener los productos y tipos de productos para los combos del formulario
    productos = obtener_productos2()
    tipos_producto = obtener_tipos_producto2()

    # Renderizar el formulario
    return render_template('panel/asignar_detalle_producto.html', productos=productos, tipos_producto=tipos_producto)


#API PARA OBTENER
@csrf.exempt
@bp.route('/api/obtener_detalle_productos', methods=['GET'])
@jwt_required()
def ape_obtener_detalle_productos():
    rpta=dict()
    try:
        productos = obtener_productos()

        if not productos:
            rpta["data"]={}
            rpta["message"]="No se logró encontrar detalles de los productos"
            rpta["status"]=-1
        else:
            rpta["data"]=productos
            rpta["message"]="Detalle de productos cargado correctamente"
            rpta["status"]=1

    except Exception as e:
        rpta["data"]={}
        rpta["message"]="Error al mostrar los detalles de los productos" + repr(e)
        rpta["status"]=0


    return jsonify(rpta)


#PARA INSERTAR

@csrf.exempt
@bp.route('/api/insertar_detalle_tipo_producto', methods=['POST'])
@jwt_required()
def api_insertar_detalle_tipo_producto():
    rpta=dict()
    try:

        id_producto = request.form.get("id_producto")
        id_tipo_producto = request.form.get("id_tipo_producto")
        stock = request.form.get("stock")
        precio = request.form.get("precio")
        imagen = request.files.get("imagen")


        if not (id_producto and id_tipo_producto and stock and precio and imagen):
            rpta["data"]={}
            rpta["message"]= "Faltan datos requeridos para insertar el detalle del producto."
            rpta["status"]= -1
        else:
            # Guardar la imagen
            filename = secure_filename(imagen.filename)
            folder='/home/grupo004/mysite/app/static/media'
            upload_path = os.path.join(folder, filename)
            imagen.save(upload_path)

            insertar_detalle_tipo_producto2(id_tipo_producto, id_producto, stock, precio, filename)
            rpta["data"] = {}
            rpta["message"] = "Detalle de tipo de producto insertado exitosamente."
            rpta["status"] = 1

    except Exception as e:
        rpta["data"]={}
        rpta["message"]="Error al insertar el detalle de producto" + repr(e)
        rpta["status"]= 0
    return jsonify(rpta)
@csrf.exempt
@bp.route('/api/editar_detalle/<int:id_producto>/<int:id_tipo_producto>', methods=['POST'])
@jwt_required()
def api_editar_detalle_tipo_producto(id_producto, id_tipo_producto):
    rpta=dict()
    try:

        stock = request.form.get('stock')
        precio = request.form.get('precio')
        estado = request.form.get('estado')
        imagen_actual = request.files.get('imagen_actual')

        if not (stock and precio and estado):
            rpta["data"]={}
            rpta["message"]="Faltan datos requeridos para actualizar el detalle del producto"
            rpta["status"]= -1
        else:
            imagen = request.files.get('imagen')
            if imagen and imagen.filename != '':
                filename = secure_filename(imagen.filename)
                folder='/home/grupo004/mysite/app/static/media'
                upload_path = os.path.join(folder, filename)
                imagen.save(upload_path)
            else:
                filename = imagen_actual  # Mantener la imagen actual si no se sube una nueva


            actualizar_detalle_tipo_producto(id_tipo_producto, id_producto, stock, precio, filename, estado)
            rpta["data"]={}
            rpta["message"]="Detalle de producto actualizado exitosamente"
            rpta["status"]= 1


    except Exception as e:
        rpta["data"]={}
        rpta["message"]="Error al actualizar el detalle del producto" + repr(e)
        rpta["status"]= 0
    return jsonify(rpta)


#API PARA ELIMINAR
@csrf.exempt
@bp.route("/api/eliminar_detalle_producto/<int:id_producto>/<int:id_tipo_producto>", methods=["POST"])
@jwt_required()
def api_eliminar_detalle_producto(id_producto, id_tipo_producto):
    rpta=dict()

    try:
        # Verificar si el producto está asociado a una venta
        asociado = verificar_asociacion_detalle_venta(id_tipo_producto, id_producto)
        if asociado:
            rpta["data"]={}
            rpta["message"]= "No se puede eliminar el producto porque está asociado a una venta."
            rpta["status"]=-1

        else:
            deta=obtener_detalle_tipo_producto(id_producto,id_tipo_producto)
            if  not deta:
                rpta["data"]={}
                rpta["message"]= "Detalle de producto no existe"
                rpta["status"]=-1
            else:
                # Intentar eliminar el producto
                eliminar_detalle_tipo_producto(id_tipo_producto, id_producto)
                rpta["data"]={}
                rpta["message"]= "Detalle de producto eliminado exitosamente"
                rpta["status"]=1

    except Exception as e:
        rpta["data"]={}
        rpta["message"]= "Error al eliminar el detalle del tipo de producto." + repr(e)
        rpta["status"]=0
    return jsonify(rpta)


#API PARA obtener por id's

@csrf.exempt
@bp.route("/api/obtener_detalle_tipo_producto_por_ids/<int:id_producto>/<int:id_tipo_producto>", methods=["GET"])
@jwt_required()
def api_obtener_detalle_tipo_producto_por_ids(id_producto, id_tipo_producto):
    rpta=dict()
    try:
        detalle=obtener_detalle_tipo_producto(id_producto,id_tipo_producto)
        if  not detalle:
            rpta["data"]={}
            rpta["message"]= "Detalle de producto no existe"
            rpta["status"]=-1
        else:
            rpta["data"]=detalle
            rpta["message"]= "Detalle de tipo producto encontrado exitosamente"
            rpta["status"]=1
    except Exception as e:
        rpta["data"]={}
        rpta["message"]= "Error al encontrar el detalle del tipo de producto." + repr(e)
        rpta["status"]=0
    return jsonify(rpta)





@csrf.exempt
@bp.route("/eliminar_detalle_producto/<int:id_producto>/<int:id_tipo_producto>", methods=["POST", "GET"])
def eliminar_detalle_producto(id_producto, id_tipo_producto):
    valor = verificar_asociacion_detalle_venta(id_tipo_producto, id_producto)
    if valor:
        flash(f"No se puede eliminar el producto porque está asociado a una venta.", "error")
    else:
        eliminado = eliminar_detalle_tipo_producto(id_tipo_producto, id_producto)
        if eliminado:
            flash("Producto eliminado con éxito.", "success")
        else:
            flash("No se pudo eliminar el producto, ocurrió un error o no existe el producto.", "error")
    return redirect(url_for('producto.panel_producto_home'))





#PARA PRODUCTO--
@csrf.exempt
@bp.route('/panel_nuestros_productos_home', methods=['GET'])
def panel_nuestros_productos_home():

    filtro_nombre = request.args.get('nombre_producto')  # Campo de búsqueda por nombre
    productos = mostrar_productos(filtro_nombre)

    return render_template('panel/producto1.html',productos=productos,filtro_nombre=filtro_nombre)



@csrf.exempt
@bp.route('/agregar_nuevo_producto')
def agregar_nuevo_producto():
    generos = obtener_generos()
    descuentos = obtener_descuentos()
    return render_template("panel/agregar_nuevo_producto.html",generos=generos,descuentos=descuentos)


@csrf.exempt
@bp.route('/guardar_producto', methods=['POST'])
def guardar_producto():
    nombre_producto = request.form['nombre_producto']
    anio_lanzamiento = request.form['anio_lanzamiento']
    descripcion = request.form['descripcion']
    estado_producto = request.form['estado_producto']
    id_descuento = request.form.get('id_descuento')
    id_genero = request.form['id_genero']


    # Verificar si el producto ya existe con el mismo tipo
    if existe_producto(nombre_producto):
        flash(f'El producto "{nombre_producto}" ya existe en la presentación seleccionada.', 'error')
        return redirect(url_for('producto.panel_nuestros_productos_home'))
    else:
        try:
            insertar_producto(nombre_producto, anio_lanzamiento,descripcion,estado_producto,id_descuento,id_genero)
            flash(f"El producto: '{nombre_producto}' fue agregado con éxito.", "success_guardar_producto")
        except Exception as e:
            flash(f"Error al guardar el producto: {e}", "error_guardar_producto")

    return redirect(url_for('producto.panel_nuestros_productos_home'))


@csrf.exempt
@bp.route('/editar_producto/<int:id_producto>', methods=['GET', 'POST'])
def editar_producto(id_producto):
    # Si es una solicitud POST, actualizar el producto
    if request.method == 'POST':

        nombre_producto = request.form['nombre_producto']
        anio_lanzamiento = request.form['anio_lanzamiento']
        descripcion = request.form['descripcion']
        estado = request.form['estado']
        id_descuento = request.form.get('id_descuento')
        id_genero = request.form['id_genero']


        actualizar_producto(id_producto, nombre_producto, anio_lanzamiento, descripcion, estado, id_descuento, id_genero)


        return redirect(url_for('producto.panel_nuestros_productos_home'))

    # Si es una solicitud GET, mostrar el formulario con datos actuales
    producto = obtener_producto_por_id(id_producto)
    generos = obtener_generos()
    descuentos = obtener_descuentos()

    print(f"Generos: {generos}")
    print(f"Descuentos: {descuentos}")

    return render_template("panel/editar_nuevo_producto.html",
                           producto=producto, generos=generos,
                           descuentos=descuentos)


@csrf.exempt
@bp.route("/dar_de_baja_producto/<int:id_producto>", methods=["POST"])
def dar_de_baja_producto_route(id_producto):
    dar_de_baja_producto(id_producto)
    return redirect(url_for('producto.panel_nuestros_productos_home'))

#------------------------------------------------------------------------------------------------
@csrf.exempt
@bp.route("/actualizar", methods=["POST"])
def actualizar_producto_route():
    id_producto = request.form["id_producto"]
    nombre_producto = request.form["nombre_producto"]
    anio_lanzamiento = request.form["anio_lanzamiento"]
    descripcion = request.form["descripcion"]
    estado_producto = request.form["estado_producto"]
    id_descuento = request.form["id_descuento"]
    id_genero = request.form["id_genero"]
    url_img = request.form["url_img"]

    # Actualiza el producto
    actualizar_producto(id_producto, nombre_producto, anio_lanzamiento, descripcion, estado_producto, id_descuento, id_genero)

    # Actualiza DETALLE_TIPO_PRODUCTO
    id_tipo_producto = request.form["id_tipo_producto"]
    stock = int(request.form["stock"])
    precio = float(request.form["precio"])
    url_img = request.form["url_img"]

    insertar_o_actualizar_detalle_tipo_producto(id_tipo_producto, id_producto, stock, precio, url_img)

    flash('Producto actualizado exitosamente', 'success')
    return redirect(url_for('producto.panel_producto_home'))

# ------------------------------------APIS PRODUCTO


@csrf.exempt
@bp.route("/APIobtener_todos", methods=["GET"])
@jwt_required()
def api_obtener_todos():
    rpta = dict()
    try:
        productos = listarProductos()
        rpta["data"] = productos
        rpta["message"] = "Listado de productos realizado correctamente"
        rpta["status"] = 1
        return jsonify(rpta)
    except Exception as e:
        rpta["data"] = {}
        rpta["message"] = "Ocurrió un error: " + repr(e)
        rpta["status"] = -1
        return jsonify(rpta)

@csrf.exempt
@bp.route('/apiguardar_producto', methods=['POST'])
@jwt_required()
def api_guardar_producto():
    rpta = dict()
    try:
        data = request.get_json()

        nombre_producto = data.get('nombre_producto')
        anio_lanzamiento = data.get('anio_lanzamiento')
        descripcion = data.get('descripcion')
        estado_producto = data.get('estado_producto')
        id_descuento = data.get('id_descuento')
        id_genero = data.get('id_genero')

        if existe_producto(nombre_producto):
            rpta["data"] = {}
            rpta["message"] = f"El producto '{nombre_producto}' ya existe"
            rpta["status"] = 0
            return jsonify(rpta)

        insertar_producto(nombre_producto, anio_lanzamiento, descripcion, estado_producto, id_descuento, id_genero)

        rpta["data"] = {}
        rpta["message"] = f"Producto '{nombre_producto}' agregado exitosamente"
        rpta["status"] = 1
        return jsonify(rpta)
    except Exception as e:
        rpta["data"] = {}
        rpta["message"] = f"Ocurrió un error inesperado: {repr(e)}"
        rpta["status"] = -1
        return jsonify(rpta)

@csrf.exempt
@bp.route('/apieditar_producto/<int:id_producto>', methods=['POST'])
@jwt_required()
def api_editar_producto(id_producto):
    rpta = dict()
    try:
        data = request.get_json()

        nombre_producto = data.get('nombre_producto')
        anio_lanzamiento = data.get('anio_lanzamiento')
        descripcion = data.get('descripcion')
        estado = data.get('estado')
        id_descuento = data.get('id_descuento')
        id_genero = data.get('id_genero')

        existe = obtener_productos_por_id(id_producto)

        if not existe:
            rpta["data"] = {}
            rpta["message"] = "Id del producto no existe"
            rpta["status"] = 0
            return jsonify(rpta)
        else:
            if existe_producto(nombre_producto):
                rpta["data"] = {}
                rpta["message"] = f"El producto '{nombre_producto}' ya existe"
                rpta["status"] = 0
                return jsonify(rpta)
            else:
                actualizar_producto(id_producto, nombre_producto, anio_lanzamiento, descripcion, estado, id_descuento, id_genero)
                rpta["data"] = {}
                rpta["message"] = f"Producto '{nombre_producto}' editado correctamente"
                rpta["status"] = 0
                return jsonify(rpta)

    except Exception as e:
        rpta["data"] = {}
        rpta["message"] = f"Ocurrió un error inesperado: {repr(e)}"
        rpta["status"] = -1
        return jsonify(rpta)


@csrf.exempt
@bp.route('/apidar_de_baja_producto/<int:id_producto>', methods=['POST'])
@jwt_required()
def api_dar_de_baja_producto(id_producto):
    rpta = dict()
    try:
        producto = obtener_productos_por_id(id_producto)
        if not producto:
            rpta["data"] = {}
            rpta["message"] = "El ID del producto no existe"
            rpta["status"] = 0
            return jsonify(rpta)

        producto = producto[0]
        if producto[4] == 'I':
            rpta["data"] = producto
            rpta["message"] = "El producto ya está dado de baja"
            rpta["status"] = 0
            return jsonify(rpta)

        dar_de_baja_producto(id_producto)

        rpta["data"] = {}
        rpta["message"] = "Producto dado de baja exitosamente"
        rpta["status"] = 1
        return jsonify(rpta)

    except Exception as e:
        rpta["data"] = {}
        rpta["message"] = f"Ocurrió un error inesperado: {repr(e)}"
        rpta["status"] = -1
        return jsonify(rpta)

@csrf.exempt
@bp.route('/apieliminar_producto/<int:id_producto>', methods=['POST'])
@jwt_required()
def api_eliminar_producto(id_producto):
    rpta = dict()
    try:

        if not obtener_productos_por_id(id_producto):
            rpta["data"] = {}
            rpta["message"] = "El producto no existe en la base de datos."
            rpta["status"] = 0
            return jsonify(rpta)

        if not validar_producto_sin_asociaciones(id_producto):
            rpta["data"] = {}
            rpta["message"] = "No se puede eliminar: el producto está asociado a otros registros."
            rpta["status"] = 0
            return jsonify(rpta)

        eliminar_producto(id_producto)
        rpta["data"] = {}
        rpta["message"] = "Producto eliminado exitosamente."
        rpta["status"] = 1
        return jsonify(rpta)

    except Exception as e:
        rpta["data"] = {}
        rpta["message"] = f"Error al eliminar producto: {repr(e)}"
        rpta["status"] = -1
        return jsonify(rpta)


@csrf.exempt
@bp.route('/apiobtenerproductoporid/<int:id_producto>', methods=['GET'])
@jwt_required()
def apiobtenerproductoporid(id_producto):
    rpta = dict()
    try:
        producto = obtener_productos_por_id(id_producto)

        if not producto:
            rpta["data"] = {}
            rpta["message"] = f"El producto con ID '{id_producto}' no existe en la base de datos."
            rpta["status"] = 0
            return jsonify(rpta)

        rpta["data"] = producto
        rpta["message"] = "El producto existe en la base de datos."
        rpta["status"] = 1
        return jsonify(rpta)

    except Exception as e:
        rpta["data"] = {}
        rpta["message"] = f"Error al validar producto por ID: {repr(e)}"
        rpta["status"] = -1
        return jsonify(rpta)

def obtener_producto_por_nombre(nombre_producto):
    conexion = obtener_conexion()
    try:
        with conexion.cursor(dictionary=True) as cursor:
            query = "SELECT * FROM PRODUCTO WHERE nombre_producto = %s"
            cursor.execute(query, (nombre_producto,))
            return cursor.fetchone()  # Devuelve un diccionario o None
    except Exception as e:
        print(f"Error al obtener producto por nombre: {e}")
        return None
    finally:

        conexion.close()
@csrf.exempt
@bp.route('/apiobtenerproductopornombre', methods=['POST'])
@jwt_required()
def apiobtenerproductopornombre():
    rpta = dict()
    try:
        data = request.get_json()
        nombre_producto = data.get('nombre_producto')

        if not nombre_producto or not nombre_producto.strip():
            rpta["data"] = {}
            rpta["message"] = "El nombre del producto es obligatorio."
            rpta["status"] = 0
            return jsonify(rpta)

        producto = obtener_producto_por_nombre1(nombre_producto)

        if not producto:
            rpta["data"] = {}
            rpta["message"] = f"No existe un producto con el nombre '{nombre_producto}'."
            rpta["status"] = 0
            return jsonify(rpta)

        rpta["data"] = producto
        rpta["message"] = "El producto existe en la base de datos."
        rpta["status"] = 1
        return jsonify(rpta)

    except Exception as e:
        rpta["data"] = {}
        rpta["message"] = f"Error al validar producto por nombre: {repr(e)}"
        rpta["status"] = -1
        return jsonify(rpta)

# ------------------------------------

@csrf.exempt
@bp.route('/editar_detalle/<int:id_producto>/<int:id_tipo_producto>', methods=['GET', 'POST'])
def editar_detalle_tipo_producto(id_producto, id_tipo_producto):
    if request.method == 'POST':
        # Recoger datos del formulario
        form_data = request.form
        stock = form_data.get('stock')
        precio = form_data.get('precio')
        estado = form_data.get('estado')
        imagen_actual = form_data.get('imagen_actual')

        # Manejo de imagen subida
        imagen = request.files.get('imagen')
        if imagen and imagen.filename != '':
            filename = secure_filename(imagen.filename)
            folder='/home/grupo004/mysite/app/static/media'
            upload_path = os.path.join(folder, filename)
            imagen.save(upload_path)
        else:
            filename = imagen_actual  # Mantener la imagen actual si no se sube una nueva

        # Actualizar el detalle en la base de datos
        if actualizar_detalle_tipo_producto(id_tipo_producto, id_producto, stock, precio, filename, estado):
            flash('Detalle de producto actualizado exitosamente', 'success')
            return redirect(url_for('producto.panel_producto_home'))
        else:
            flash('Error al actualizar el detalle de producto', 'error')

    # Obtener los datos actuales del detalle del producto
    detalle_producto = obtener_detalle_producto(id_producto, id_tipo_producto)

    return render_template('panel/editar_producto.html', detalle_producto=detalle_producto)













