# control_carrito.py
from decimal import Decimal
from app.bd import get_db_connection
from datetime import date, timedelta, datetime
import random
import string
import pymysql

def obtener_detalles_producto(product_id, tipo_producto_id):
    """Obtiene los detalles de un producto específico"""
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = """
            SELECT
                P.ID_PRODUCTO,
                P.NOMBRE_PRODUCTO,
                DTP.PRECIO,
                DTP.ID_TIPO_PRODUCTO,
                DTP.STOCK,
                TP.NOMBRE_TIPO_PRODUCTO,
                IFNULL(D.PORCENTAJE, 0) AS DESCUENTO,
                ROUND((DTP.PRECIO - (DTP.PRECIO * D.PORCENTAJE / 100)), 2) AS PRECIO_CON_DESCUENTO
            FROM PRODUCTO P
            JOIN DETALLE_TIPO_PRODUCTO DTP ON P.ID_PRODUCTO = DTP.ID_PRODUCTO
            JOIN TIPO_PRODUCTO TP ON DTP.ID_TIPO_PRODUCTO = TP.ID_TIPO_PRODUCTO
            LEFT JOIN DESCUENTO D ON P.ID_DESCUENTO = D.ID_DESCUENTO
            WHERE P.ID_PRODUCTO = %s AND DTP.ID_TIPO_PRODUCTO = %s
            """
            cursor.execute(sql, (product_id, tipo_producto_id))
            producto = cursor.fetchone()
            if producto:
                columnas = [column[0] for column in cursor.description]
                producto = dict(zip(columnas, producto))
        return producto
    except Exception as e:
        print(f"Error al obtener detalles del producto: {e}")
        return None
    finally:
        connection.close()

def verificar_producto_en_carrito(usuario_id, product_id, tipo_producto_id):
    """Verifica si un producto ya está en el carrito del usuario"""
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql_cart_check = """
                SELECT C.ID_CARRITO, C.CANTIDAD
                FROM CARRITO C
                WHERE C.ID_USUARIO = %s AND C.ID_PRODUCTO = %s AND C.ID_TIPO_PRODUCTO = %s AND C.ESTADO = 'A'
            """
            cursor.execute(sql_cart_check, (usuario_id, product_id, tipo_producto_id))
            carrito_item = cursor.fetchone()
            if carrito_item:
                columnas = [column[0] for column in cursor.description]
                carrito_item = dict(zip(columnas, carrito_item))

        return carrito_item
    except Exception as e:
        print(f"Error al verificar producto en carrito: {e}")
        return None
    finally:
        connection.close()

def agregar_producto_a_carrito(usuario_id, tipo_producto_id, product_id, cantidad, precio_con_descuento, monto):
    """Agrega un nuevo producto al carrito o actualiza uno existente"""
    connection = get_db_connection()
    try:
        # Verificar si el producto ya está en el carrito
        carrito_item = verificar_producto_en_carrito(usuario_id, product_id, tipo_producto_id)

        with connection.cursor() as cursor:
            if carrito_item:
                # Si el producto ya está en el carrito, actualizar la cantidad
                nueva_cantidad = carrito_item['CANTIDAD'] + cantidad
                sql_update_cart = """
                UPDATE CARRITO SET CANTIDAD = %s, MONTO = %s
                WHERE ID_CARRITO = %s
                """
                cursor.execute(sql_update_cart, (nueva_cantidad, nueva_cantidad * precio_con_descuento * Decimal(1.18), carrito_item['ID_CARRITO']))
            else:
                # Insertar nuevo producto en el carrito del usuario
                sql_add_cart = """
                INSERT INTO CARRITO (ID_USUARIO, ID_TIPO_PRODUCTO, ID_PRODUCTO, CANTIDAD, PRECIO, MONTO, ESTADO)
                VALUES (%s, %s, %s, %s, %s, %s, 'A')
                """
                cursor.execute(sql_add_cart, (usuario_id, tipo_producto_id, product_id, cantidad, precio_con_descuento, monto))

        connection.commit()
        return True
    except Exception as e:
        connection.rollback()
        print(f"Error al agregar producto al carrito: {e}")
        return False
    finally:
        connection.close()


def verificar_producto_carrito(usuario_id, product_id, tipo_producto_id):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = """
                SELECT C.ID_CARRITO, DTP.STOCK
                FROM CARRITO C
                JOIN DETALLE_TIPO_PRODUCTO DTP ON C.ID_PRODUCTO = DTP.ID_PRODUCTO AND C.ID_TIPO_PRODUCTO = DTP.ID_TIPO_PRODUCTO
                WHERE C.ID_USUARIO = %s AND C.ID_PRODUCTO = %s AND C.ID_TIPO_PRODUCTO = %s AND C.ESTADO = 'A'
            """
            cursor.execute(sql, (usuario_id, product_id, tipo_producto_id))
            producto_carrito = cursor.fetchone()
            if producto_carrito:
                columnas = [column[0] for column in cursor.description]
                producto_carrito = dict(zip(columnas, producto_carrito))

        return producto_carrito
    finally:
        connection.close()

def actualizar_cantidad_carrito(id_carrito, nueva_cantidad):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = """
                UPDATE CARRITO SET CANTIDAD = %s, MONTO = PRECIO * %s * 1.18
                WHERE ID_CARRITO = %s
            """
            cursor.execute(sql, (nueva_cantidad, nueva_cantidad, id_carrito))
        connection.commit()
    finally:
        connection.close()

def eliminar_producto_carrito(usuario_id, product_id, tipo_producto_id):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = """
                DELETE FROM CARRITO
                WHERE ID_USUARIO = %s AND ID_PRODUCTO = %s AND ID_TIPO_PRODUCTO = %s AND ESTADO = 'A'
            """
            cursor.execute(sql, (usuario_id, product_id, tipo_producto_id))
        connection.commit()
    finally:
        connection.close()

def vaciar_carrito(usuario_id):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = """
                DELETE FROM CARRITO
                WHERE ID_USUARIO = %s AND ESTADO = 'A'
            """
            cursor.execute(sql, (usuario_id,))
        connection.commit()
    finally:
        connection.close()

def obtener_items_carrito(usuario_id):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = """
                SELECT
                    C.ID_PRODUCTO,
                    P.NOMBRE_PRODUCTO,
                    TP.NOMBRE_TIPO_PRODUCTO,
                    C.CANTIDAD,
                    DTP.PRECIO,
                    IFNULL(D.PORCENTAJE, 0) AS DESCUENTO,
                    ROUND((DTP.PRECIO - (DTP.PRECIO * D.PORCENTAJE / 100)), 2) AS PRECIO_CON_DESCUENTO,
                    ROUND((DTP.PRECIO - (DTP.PRECIO * D.PORCENTAJE / 100)) * C.CANTIDAD, 2) AS TOTAL_CON_DESCUENTO,
                    ROUND(((DTP.PRECIO - (DTP.PRECIO * D.PORCENTAJE / 100)) * C.CANTIDAD) * 1.18, 2) AS PRECIO_FINAL_CON_IGV,
                    C.MONTO,
                    C.ID_TIPO_PRODUCTO,
                    DTP.URL_IMG
                FROM
                    CARRITO C
                JOIN
                    PRODUCTO P ON C.ID_PRODUCTO = P.ID_PRODUCTO
                JOIN
                    TIPO_PRODUCTO TP ON C.ID_TIPO_PRODUCTO = TP.ID_TIPO_PRODUCTO
                JOIN
                    DETALLE_TIPO_PRODUCTO DTP ON C.ID_PRODUCTO = DTP.ID_PRODUCTO AND C.ID_TIPO_PRODUCTO = DTP.ID_TIPO_PRODUCTO
                LEFT JOIN
                    DESCUENTO D ON P.ID_DESCUENTO = D.ID_DESCUENTO
                WHERE
                    C.ID_USUARIO = %s AND C.ESTADO = 'A';
            """
            cursor.execute(sql, (usuario_id,))
            cart = cursor.fetchall()

            columnas = [column[0] for column in cursor.description]
            cart = [dict(zip(columnas, fila)) for fila in cart]

            total = sum(item['PRECIO_FINAL_CON_IGV'] for item in cart)
            return cart, total
    finally:
        connection.close()



def obtener_carrito_checkout(usuario_id):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = """
                SELECT
                    C.ID_PRODUCTO,
                    P.NOMBRE_PRODUCTO,
                    TP.ID_TIPO_PRODUCTO,
                    TP.NOMBRE_TIPO_PRODUCTO,
                    C.CANTIDAD,
                    DTP.PRECIO,
                    IFNULL(D.PORCENTAJE, 0) AS DESCUENTO,
                    ROUND((DTP.PRECIO - (DTP.PRECIO * D.PORCENTAJE / 100)), 2) AS PRECIO_CON_DESCUENTO,
                    ROUND(((DTP.PRECIO - (DTP.PRECIO * D.PORCENTAJE / 100)) * C.CANTIDAD) * 1.18, 2) AS PRECIO_FINAL_CON_IGV
                FROM
                    CARRITO C
                JOIN
                    PRODUCTO P ON C.ID_PRODUCTO = P.ID_PRODUCTO
                JOIN
                    TIPO_PRODUCTO TP ON C.ID_TIPO_PRODUCTO = TP.ID_TIPO_PRODUCTO
                JOIN
                    DETALLE_TIPO_PRODUCTO DTP ON C.ID_PRODUCTO = DTP.ID_PRODUCTO AND C.ID_TIPO_PRODUCTO = DTP.ID_TIPO_PRODUCTO
                LEFT JOIN
                    DESCUENTO D ON P.ID_DESCUENTO = D.ID_DESCUENTO
                WHERE
                    C.ID_USUARIO = %s AND C.ESTADO = 'A';
            """
            cursor.execute(sql, (usuario_id,))
            carrito = cursor.fetchall()

            columnas = [column[0] for column in cursor.description]
            carrito = [dict(zip(columnas, fila)) for fila in carrito]

            monto_pantalla = sum(item['PRECIO_FINAL_CON_IGV'] for item in carrito)
            return carrito, monto_pantalla
    finally:
        connection.close()

def insertar_tarjeta(usuario_id, tipo_tarjeta, numero_tarjeta, fecha_expiracion, cvv):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            check_sql = "SELECT ID_TARJETA FROM TARJETA WHERE ID_USUARIO = %s AND NUMERO_TARJETA = %s"
            cursor.execute(check_sql, (usuario_id, numero_tarjeta))
            existing_tarjeta = cursor.fetchone()

            if existing_tarjeta:
                # Si ya existe, devolver el ID existente
                return existing_tarjeta[0]

            # Si no existe, insertar nueva tarjeta
            sql = """
                INSERT INTO TARJETA (ID_USUARIO, TIPO_TARJETA, NUMERO_TARJETA, FECHA_EXPIRACION, CVV, ESTADO_TARJETA)
                VALUES (%s, %s, %s, %s, %s, 'A')
            """
            cursor.execute(sql, (usuario_id, tipo_tarjeta, numero_tarjeta, fecha_expiracion, cvv))
            connection.commit()
            return cursor.lastrowid
    except Exception as e:
        connection.rollback()
        raise Exception(f"Error al insertar tarjeta: {e}")
    finally:
        connection.close()

def procesar_venta(usuario_id, tarjeta_id, monto_pantalla, total_con_envio, carrito, direccion, provincia, ciudad):
    connection = get_db_connection()
    cursor = None
    cantidad_stock = 0
    try:
        connection.begin()  # Iniciar transacción explícitamente
        cursor = connection.cursor()

        # Insertar venta
        sql_venta = """
            INSERT INTO VENTA (ID_USUARIO, ID_TARJETA, FECHA_HORA, ESTADO, SUBTOTAL, IGV, TOTAL)
            VALUES (%s, %s, NOW(), 'P', %s, 0.18, %s)
        """
        cursor.execute(sql_venta, (usuario_id, tarjeta_id, monto_pantalla, total_con_envio))
        venta_id = cursor.lastrowid

        print("Se insertó venta")

        # Insertar detalles de la venta
        sql_detalle = """
            INSERT INTO DETALLE_VENTA
            (ID_VENTA, ID_TIPO_PRODUCTO, ID_PRODUCTO, CANTIDAD, PRECIO, ESTADO, SUBTOTAL, IGV)
            VALUES (%s, %s, %s, %s, %s, 'A', %s, %s)
        """
        for item in carrito:
            subtotal = Decimal(item['PRECIO_CON_DESCUENTO'] * item['CANTIDAD'])
            igv = subtotal * Decimal('0.18')
            cursor.execute(sql_detalle, (
                venta_id,
                item['ID_TIPO_PRODUCTO'],
                item['ID_PRODUCTO'],
                item['CANTIDAD'],
                Decimal(item['PRECIO_CON_DESCUENTO']),
                subtotal,
                igv
            ))

        for item in carrito:
            cantidad_stock = item['CANTIDAD']

        print("Se insertó detalle venta")


        # Actualizar el stock para cada producto en el carrito
        sql_actualizar_stock = """
            UPDATE DETALLE_TIPO_PRODUCTO
            SET STOCK = STOCK - %s
            WHERE ID_PRODUCTO = %s AND ID_TIPO_PRODUCTO = %s
        """

        for item in carrito:
            cantidad_stock = item['CANTIDAD']
            id_producto = item['ID_PRODUCTO']
            id_tipo_producto = item['ID_TIPO_PRODUCTO']

            # Verificar si el stock actual es suficiente antes de restar
            cursor.execute("SELECT STOCK FROM DETALLE_TIPO_PRODUCTO WHERE ID_PRODUCTO = %s AND ID_TIPO_PRODUCTO = %s",
                           (id_producto, id_tipo_producto))
            stock_actual = cursor.fetchone()[0]

            if stock_actual >= cantidad_stock:
                cursor.execute(sql_actualizar_stock, (cantidad_stock, id_producto, id_tipo_producto))
            else:
                raise Exception(f"No hay suficiente stock para el producto {id_producto}")


        print("Se actualizó el stock de los productos")

        # Generar dirección de envío
        direccion_envio = f"{direccion}, {provincia}, {ciudad}"

        # Generar envío
        fecha_envio = date.today()
        fecha_entrega = fecha_envio + timedelta(days=5)
        numero_seguimiento = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

        sql_envio = """
            INSERT INTO ENVIO (ID_VENTA, DIRECCION_ENVIO, FECHA_ENVIO, FECHA_ENTREGA, ESTADO_ENVIO, NUMERO_SEGUIMIENTO, PRECIO)
            VALUES (%s, %s, %s, %s, 'P', %s, 10.00)
        """
        cursor.execute(sql_envio, (venta_id, direccion_envio, fecha_envio, fecha_entrega, numero_seguimiento))

        print("Se insertó envio")


        sql_get_last_correlativo = """
            SELECT CORRELATIVO FROM COMPROBANTE ORDER BY ID_COMPROBANTE DESC LIMIT 1
        """
        cursor.execute(sql_get_last_correlativo)
        last_correlativo = cursor.fetchone()

        # Cambiar a acceso por índice (0) en lugar de clave de diccionario
        new_correlativo = '0000000001' if not last_correlativo else str(int(last_correlativo[0]) + 1).zfill(10)

        serie = 'F001'


        sql_comprobante = """
            INSERT INTO COMPROBANTE (ID_VENTA, FECHA_EMISION, TIPO_COMPROBANTE, TOTAL, SERIE, CORRELATIVO)
            VALUES (%s, NOW(), 'B', %s, %s, %s)
        """
        
        cursor.execute(sql_comprobante, (venta_id, total_con_envio, serie, new_correlativo))

        print("Se insertó comprobante")

        connection.commit()
        return venta_id

    except Exception as e:
        connection.rollback()
        print(f"Error al procesar la venta: {e}")
        raise

    finally:
        cursor.close()
        connection.close()


def obtener_carritos():
    connection = get_db_connection()
    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = """
                SELECT C.ID_CARRITO, U.NOMBRE_USUARIO, P.NOMBRE_PRODUCTO, C.CANTIDAD, C.PRECIO, C.MONTO FROM CARRITO C
                INNER JOIN USUARIO U ON U.ID_USUARIO = C.ID_USUARIO
                INNER JOIN DETALLE_TIPO_PRODUCTO DTP ON DTP.ID_PRODUCTO = C.ID_PRODUCTO
                INNER JOIN PRODUCTO P ON P.ID_PRODUCTO = DTP.ID_PRODUCTO
                WHERE C.ESTADO = 'A'
            """
            cursor.execute(sql)
            carritos = cursor.fetchall()
            return carritos
    finally:
        connection.close()
        
def obtener_carrito_usuario(id_usuario):
    connection = get_db_connection()
    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = """
                SELECT C.ID_CARRITO, U.NOMBRE_USUARIO, P.NOMBRE_PRODUCTO, C.CANTIDAD, C.PRECIO, C.MONTO FROM CARRITO C
                INNER JOIN USUARIO U ON U.ID_USUARIO = C.ID_USUARIO
                INNER JOIN DETALLE_TIPO_PRODUCTO DTP ON DTP.ID_PRODUCTO = C.ID_PRODUCTO
                INNER JOIN PRODUCTO P ON P.ID_PRODUCTO = DTP.ID_PRODUCTO
                WHERE C.ESTADO = 'A' AND C.ID_USUARIO = %s
            """
            cursor.execute(sql, (id_usuario,))
            carritos = cursor.fetchall()
            return carritos
    finally:
        connection.close()