import pymysql
from app.bd import get_db_connection
from datetime import datetime, timedelta
import random
from app import csrf

@csrf.exempt
def get_products(filters=None):
    conn = get_db_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = """
            SELECT p.ID_PRODUCTO, p.NOMBRE_PRODUCTO, p.DESCRIPCION,
                   tp.NOMBRE_TIPO_PRODUCTO, g.NOMBRE_GENERO, dtp.PRECIO,
                   dtp.URL_IMG, d.PORCENTAJE
            FROM PRODUCTO p
            JOIN DETALLE_TIPO_PRODUCTO dtp ON p.ID_PRODUCTO = dtp.ID_PRODUCTO
            JOIN TIPO_PRODUCTO tp ON dtp.ID_TIPO_PRODUCTO = tp.ID_TIPO_PRODUCTO
            JOIN GENERO g ON p.ID_GENERO = g.ID_GENERO
            LEFT JOIN DESCUENTO d ON p.ID_DESCUENTO = d.ID_DESCUENTO
            WHERE 1=1
            """
            params = []

            if filters:
                if filters.get('tipo'):
                    sql += " AND tp.NOMBRE_TIPO_PRODUCTO = %s"
                    params.append(filters['tipo'])
                if filters.get('genero'):
                    sql += " AND g.ID_GENERO = %s"
                    params.append(filters['genero'])

            cursor.execute(sql, params)
            products = cursor.fetchall()
            return products
    finally:
        conn.close()

@csrf.exempt
def get_genres():
    conn = get_db_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("SELECT ID_GENERO, NOMBRE_GENERO FROM GENERO WHERE ESTADO_GENERO = 'A'")
            genres = cursor.fetchall()
            return genres
    finally:
        conn.close()

@csrf.exempt
def get_sales_count():
    conn = get_db_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = "SELECT COUNT(*) AS cantidad_ventas FROM VENTA"
            cursor.execute(sql)
            result = cursor.fetchone()
            return result['cantidad_ventas']
    finally:
        conn.close()

@csrf.exempt
def get_total_shipments():
    conn = get_db_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = "SELECT COUNT(*) AS total_envios FROM ENVIO"
            cursor.execute(sql)
            result = cursor.fetchone()
            return result['total_envios']
    finally:
        conn.close()


@csrf.exempt
def get_total_users():
    conn = get_db_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = "SELECT COUNT(*) AS total_usuarios FROM USUARIO"
            cursor.execute(sql)
            result = cursor.fetchone()
            return result['total_usuarios']
    finally:
        conn.close()

@csrf.exempt
def list_sales():
    conn = get_db_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = "SELECT * FROM VENTA"
            cursor.execute(sql)
            sales = cursor.fetchall()
            return sales
    finally:
        conn.close()

@csrf.exempt
def get_recent_sales():
    conn = get_db_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = """
            SELECT V.ID_VENTA, U.NOMBRES, U.APELLIDO_PAT, V.FECHA_HORA, V.ESTADO, V.TOTAL
            FROM VENTA V
            JOIN USUARIO U ON V.ID_USUARIO = U.ID_USUARIO
            ORDER BY V.FECHA_HORA DESC
            LIMIT 5
            """
            cursor.execute(sql)
            recent_sales = cursor.fetchall()
            return recent_sales
    finally:
        conn.close()

### SECCIÓN DE ENVIOS ###
def generarFechaEnvio():
    fechaActual = datetime.now().date()
    fechaEnvio = fechaActual + timedelta(days=1)
    return fechaEnvio

def generarFechaEntrega():
    fechaEnvio = generarFechaEnvio()
    aumentar = random.randint(5,10)
    fechaEntrega = fechaEnvio + timedelta(days=aumentar)
    return fechaEntrega

def generarNumSeguimiento():
    numSeguimiento = random.randint(11111111,99999999)
    return numSeguimiento


#Funciones del controlador
def insertarEnvio(idVenta, direccion, precio):
    fechaEnvio = generarFechaEnvio()
    fechaEntrega = generarFechaEntrega()
    numSeguimiento = generarNumSeguimiento()
    estado = 'P'

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
            INSERT INTO ENVIO (ID_VENTA, DIRECCION_ENVIO, FECHA_ENVIO, FECHA_ENTREGA, ESTADO_ENVIO, NUMERO_SEGUIMIENTO, PRECIO)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (idVenta, direccion, fechaEnvio, fechaEntrega, estado, numSeguimiento, precio))
        conn.commit()
    except Exception as e:
        print(f"Error inserting shipment: {e}")
        conn.rollback()
    finally:
        conn.close()


def modificarEnvio(idVenta, direccion, fechaEnvio, fechaEntrega, estado, numSeguimiento, idEnvio):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
            UPDATE ENVIO
            SET ID_VENTA = %s, DIRECCION_ENVIO = %s, FECHA_ENVIO = %s, FECHA_ENTREGA = %s, ESTADO_ENVIO = %s, NUMERO_SEGUIMIENTO = %s
            WHERE ID_ENVIO = %s
            """
            cursor.execute(sql, (idVenta, direccion, fechaEnvio, fechaEntrega, estado, numSeguimiento, idEnvio))
        conn.commit()
    except Exception as e:
        print(f"Error updating shipment: {e}")
        conn.rollback()
    finally:
        conn.close()



def eliminarEnvio(idEnvio):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = "DELETE FROM ENVIO WHERE ID_ENVIO = %s"
            cursor.execute(sql, (idEnvio,))
        conn.commit()
    except Exception as e:
        print(f"Error deleting shipment: {e}")
        conn.rollback()
    finally:
        conn.close()



def obtenerTodosEnvios():
    conn = get_db_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = "SELECT * FROM ENVIO ORDER BY ID_ENVIO DESC"
            cursor.execute(sql)
            envios = cursor.fetchall()
            return envios
    finally:
        conn.close()



def obtenerEnvioID(idEnvio):
    conn = get_db_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = "SELECT * FROM ENVIO WHERE ID_ENVIO = %s"
            cursor.execute(sql, (idEnvio,))
            envio = cursor.fetchone()
            return envio
    finally:
        conn.close()



#Funciones para los cambios de estados:
#   (P)endiente = al ser la fecha de envío una día dsps del actual, siempre comienza en pendiente
#   (T)en tránsito = cuando se encuentra entre las fechas de envío y entrega
#   (E)ntregado = cuando llega la fecha de entrega en adelante
#   (C)ancelado = si se cancela la venta por algo, tmb se cancela el envío

def cambiarEstadoTransito(idEnvio):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
            UPDATE ENVIO
            SET ESTADO_ENVIO = 'T'
            WHERE ID_ENVIO = %s
            """
            cursor.execute(sql, (idEnvio,))
        conn.commit()
    except Exception as e:
        print(f"Error changing to 'In transit': {e}")
        conn.rollback()
    finally:
        conn.close()


def cambiarEstadoEntregado(idEnvio):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
            UPDATE ENVIO
            SET ESTADO_ENVIO = 'E'
            WHERE ID_ENVIO = %s
            """
            cursor.execute(sql, (idEnvio,))
        conn.commit()
    except Exception as e:
        print(f"Error changing to 'Delivered': {e}")
        conn.rollback()
    finally:
        conn.close()



def cambiarEstadoCancelado(idEnvio):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = "UPDATE ENVIO SET ESTADO_ENVIO = 'C' WHERE ID_ENVIO = %s"
            cursor.execute(sql, (idEnvio,))
        conn.commit()
    except Exception as e:
        print(f"Error changing to 'Cancelled': {e}")
        conn.rollback()
    finally:
        conn.close()


### Funciones Generales ###
def cambiarEstadoTransitoGeneral():
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
            UPDATE ENVIO
            SET ESTADO_ENVIO = 'T'
            WHERE ESTADO_ENVIO = 'P' AND CURDATE() >= FECHA_ENVIO AND CURDATE() < FECHA_ENTREGA
            """
            cursor.execute(sql)
        conn.commit()
    except Exception as e:
        print(f"Error changing to 'In transit': {e}")
        conn.rollback()
    finally:
        conn.close()


def cambiarEstadoEntregadoGeneral():
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
            UPDATE ENVIO
            SET ESTADO_ENVIO = 'E'
            WHERE ESTADO_ENVIO = 'T' AND CURDATE() >= FECHA_ENTREGA
            """
            cursor.execute(sql)
        conn.commit()
    except Exception as e:
        print(f"Error changing to 'Delivered': {e}")
        conn.rollback()
    finally:
        conn.close()


def cambiarEstadoCanceladoGeneral():
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = "UPDATE ENVIO SET ESTADO_ENVIO = 'C' WHERE ESTADO_ENVIO != 'C'"
            cursor.execute(sql)
        conn.commit()
    except Exception as e:
        print(f"Error changing to 'Cancelled': {e}")
        conn.rollback()
    finally:
        conn.close()


