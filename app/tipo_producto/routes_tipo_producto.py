from flask import Blueprint, render_template,request,redirect,url_for,flash,jsonify
from werkzeug.utils import secure_filename
from .control_tipo_producto import (obtener_tipos,insertar_tipo,actualizar_tipo,eliminar_tipo,obtener_por_id_tipo,verificarExistencia,dar_de_baja_tipo,obtener_tipos_de_producto,buscar_por_nombre
                                    )

import os
from datetime import datetime
from app import csrf
from flask_jwt_extended import jwt_required, get_jwt_identity

bp = Blueprint('tipo_producto', __name__,url_prefix='/tipo_producto')


@csrf.exempt
@bp.route('/panel_tipos_producto')
def panel_tipos_producto():
    filtro_nombre=request.args.get('nombre_tipo_producto')

    tipos=obtener_tipos(filtro_nombre)
    return render_template('panel/tipos_producto.html',tipos=tipos)

@csrf.exempt
@bp.route('/agregar_tipo_producto')
def agregar_tipo_producto():
    return render_template('panel/agregarTipoProducto.html')

@csrf.exempt
@bp.route('/guardar_tipo_producto', methods=['POST'])
def guardar_tipo_producto():
    nombre=request.form['nombre']
    estado=request.form['estado']
    if verificarExistencia(nombre):
        flash('El tipo de producto ya existe','error')
    else:
        insertar_tipo(nombre,estado)
        flash('El tipo de producto ha sido guardado exitosamente.', 'success')
    return redirect(url_for('tipo_producto.panel_tipos_producto'))

@csrf.exempt
@bp.route('/editar_tipo_producto/<int:id>', methods=['GET','POST'])
def editar_tipo_producto(id):

    if request.method == 'POST':
        nombre = request.form['nombreTipo']
        estado = request.form['estado_tipo']
        idTip = request.form['id_tipo']

        tipo_actual = obtener_por_id_tipo(idTip)
        # Si el nombre no ha cambiado, simplemente actualiza el estado

        if tipo_actual and tipo_actual[1] == nombre:
            actualizar_tipo(idTip, nombre, estado)
            flash('El tipo de producto ha sido actualizado exitosamente.', 'success_actualizar_tipo_producto')
        elif verificarExistencia(nombre):
            flash('El tipo de producto ya existe', 'error')
        else:
            actualizar_tipo(idTip, nombre, estado)
            flash('El tipo de producto ha sido actualizado exitosamente.', 'success_actualizar_tipo_producto')

        print(f"Datos recibidos - ID: {idTip}, Nombre: {nombre}, Estado: {estado}")

        return redirect(url_for('tipo_producto.panel_tipos_producto'))

    tipo = obtener_por_id_tipo(id)
    return render_template("panel/editar_tipo_producto.html", tipo=tipo)


@csrf.exempt
@bp.route('/eliminar_tipo_producto/<int:id>',methods=['POST'])
def eliminar_tipo_producto(id):
    tipo=eliminar_tipo(id)
    if  tipo:
        flash('Tipo de producto eliminado correctamente','success')
    else:
        flash('No se puede eliminar este tipo porque está referenciado en otra tabla' ,'error')

    return redirect(url_for('tipo_producto.panel_tipos_producto'))


@csrf.exempt
@bp.route('/dar_de_baja/<int:id_tipo>',methods=['POST'])
def dar_de_baja(id):
    dar_de_baja_tipo(id)
    flash('Tipo de producto dado de baja correctamente')
    return redirect(url_for('tipo_producto.panel_tipos_producto'))




@csrf.exempt
@bp.route('/api/obtener_tipos_de_producto',methods=['GET'])
@jwt_required()
def api_obtener_tipos_de_producto():
    rpta=dict()

    try:
        tipos= obtener_tipos_de_producto()


        rpta["data"]=tipos
        rpta["message"]="Listado obtenido correctamente"
        rpta["status"]=1


        return jsonify(rpta)
    except Exception as e:
        rpta["data"]={}
        rpta["message"]="Error al obtener los tipos" + repr(e)
        rpta["status"]=0
        return jsonify(rpta)

@csrf.exempt
@bp.route('/api/insertar_tipo_producto' ,methods=['POST'])
@jwt_required()
def api_insertar_tipo_producto():
    rpta=dict()
    try:
        nombre=request.json.get("nombre_tipo")
        estao=request.json.get("estado")
        valor=verificarExistencia(nombre)

        if not nombre or not estao:
            rpta["data"]={}
            rpta["message"]="Ingrese los datos correspondientes"
            rpta["status"]=-1
        elif (valor):
            rpta["data"]={}
            rpta["message"]="Tipo de producto ya existe"
            rpta["status"]=-1
        else:
            insertar_tipo(nombre,estao)
            rpta["data"]={}
            rpta["message"]="Tipo de producto insertado correctamente"
            rpta["status"]=1
    except Exception as e:
        rpta["data"]={}
        rpta["message"]="Error al insertar nuevo tipo de producto" + repr(e)
        rpta["status"]=0

    return jsonify(rpta)

@csrf.exempt
@bp.route('/api/dar_baja_tipo_producto/<int:id_tipo>', methods=["POST"])
@jwt_required()
def api_dar_baja_tipo_producto(id_tipo):
    rpta=dict()
    try:

        tipo=obtener_por_id_tipo(id_tipo)
        if  not tipo:
            rpta["data"]={}
            rpta["message"]="Tipo de producto no encontrado"
            rpta["status"]=-1
        elif tipo[2]=="I":
            rpta["data"]={}
            rpta["message"]="Tipo de producto ya se encuentra inactivo"
            rpta["status"]=-1
        else:
            dar_de_baja_tipo(id_tipo)
            rpta["data"]=tipo
            rpta["message"]="Tipo de producto dado de baja correctamente"
            rpta["status"]=1
    except Exception as e:
        rpta["data"]=tipo
        rpta["message"]="Error al dar de baja " +repr(e)
        rpta["status"]=0
    return jsonify(rpta)

@csrf.exempt
@bp.route('/api/editar_tipo_producto/<int:id_tipo>', methods=["POST"])
@jwt_required()
def api_editar_tipo_producto(id_tipo):
    rpta=dict()
    try:
        nombre=request.json.get("nombre_tipo")
        estao=request.json.get("estado")

        tipo=obtener_por_id_tipo(id_tipo)
        if  not tipo:
            rpta["data"]={}
            rpta["message"]="Tipo de producto no encontrado"
            rpta["status"]=-1
        else:
            actualizar_tipo(id_tipo,nombre,estao)
            rpta["data"]=tipo
            rpta["message"]="Tipo de producto actualizado correctamente"
            rpta["status"]=1
    except Exception as e:
        rpta["data"]={}
        rpta["message"]="Error al actualizar tipo de producto" + repr(e)
        rpta["status"]=0
    return jsonify(rpta)

@csrf.exempt
@bp.route('api/eliminar_tipo_producto/<int:id_tipo>',methods=["POST"])
@jwt_required()
def api_eliminar_tipo_producto(id_tipo):
    rpta=dict()
    try:
        tipo=obtener_por_id_tipo(id_tipo)
        if  not tipo:
            rpta["data"]={}
            rpta["message"]="Tipo de producto no encontrado"
            rpta["status"]=-1
        else:
            if eliminar_tipo(id_tipo):
                rpta["data"]={}
                rpta["message"]="Tipo de producto eliminado correctamente"
                rpta["status"]=1
            else:
                rpta["data"]={}
                rpta["message"]="Tipo de producto no se puede eliminar porque se encuentra referenciado en otra tabla"
                rpta["status"]=-1

    except Exception as e:
        rpta["data"]={}
        rpta["message"]="Error al eliminar el tipo de producto "+ repr(e)
        rpta["status"]=0
    return jsonify(rpta)


@csrf.exempt
@bp.route('/api/buscar_por_nombre', methods =["POST"])
@jwt_required()
def buscar_tipo_por_nombre():
    rpta=dict()
    try:
        nombre=request.json.get("nombre_tipo")

        if  not nombre:
            rpta["data"]={}
            rpta["message"]="Debe ingresar un nombre para realizar la búsqueda"
            rpta["status"]=-1
        else:
            tipo=buscar_por_nombre(nombre)
            if  not tipo:
                rpta["data"]={}
                rpta["message"]="No se encontró un tipo de producto con ese nombre"
                rpta["status"]=-1
            else:
                rpta["data"]=tipo
                rpta["message"]="Se encontró el tipo de producto correctamente"
                rpta["status"]=1

    except Exception as e:
        rpta["data"]={}
        rpta["message"]="Erro al buscar el tipo de producto" + repr(e)
        rpta["status"]=0
    return jsonify(rpta)


@csrf.exempt
@bp.route('/api/obtener_tipo_producto_por_id/<int:tipo_id>', methods=["GET"])
@jwt_required()
def api_obtener_tipo_producto_por_id(tipo_id):
    rpta=dict()
    try:
        tipo=obtener_por_id_tipo(tipo_id)

        if not tipo:
            rpta["data"]={}
            rpta["message"]="No se encontró un tipo de producto con ese ID"
            rpta["status"]=-1
        else:
            rpta["data"]=tipo
            rpta["message"]="Se logró encontrar el tipo de producto con dicha ID correctamente"
            rpta["status"]=1
    except Exception as e:
        rpta["data"]={}
        rpta["message"]="Error al buscar por ID el tipo de producto -->" +repr(e)
        rpta["status"]=0
    return jsonify(rpta)