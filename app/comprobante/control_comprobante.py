import pymysql
from app.bd import get_db_connection

def obtenerTodosComprobantes(estado=None):
    """
    Obtiene todos los comprobantes (activos e inactivos).
    Si se pasa un estado (A o I), filtra los comprobantes por su estado.
    """
    conn = get_db_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = """
            SELECT C.ID_COMPROBANTE,
                   C.FECHA_EMISION,
                   C.TIPO_COMPROBANTE,
                   C.TOTAL,
                   CONCAT(C.SERIE, '-', C.CORRELATIVO) AS SERIE_CORRELATIVO,
                   CONCAT(U.NOMBRES, ' ', U.APELLIDO_PAT, ' ', U.APELLIDO_MAT) AS NOMBRE_COMPLETO,
                   C.ESTADO
            FROM COMPROBANTE C
            INNER JOIN VENTA V ON V.ID_VENTA = C.ID_VENTA
            INNER JOIN USUARIO U ON U.ID_USUARIO = V.ID_USUARIO
            ORDER BY C.ID_COMPROBANTE DESC
            """

            # Si se proporciona un estado, añadirlo al WHERE de la consulta
            if estado:
                sql += " WHERE C.ESTADO = %s"
                cursor.execute(sql, (estado,))
            else:
                cursor.execute(sql)

            comprobantes = cursor.fetchall()
            return comprobantes
    except pymysql.MySQLError as e:
        print(f"Error en la consulta SQL: {e}")
        return []
    finally:
        conn.close()




def obtenerProductosPorComprobante(id_comprobante):

    conn = get_db_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = """
            SELECT P.NOMBRE_PRODUCTO, P.DESCRIPCION, DV.CANTIDAD, DV.SUBTOTAL
            FROM DETALLE_VENTA DV
            INNER JOIN PRODUCTO P ON P.ID_PRODUCTO = DV.ID_PRODUCTO
            INNER JOIN COMPROBANTE C ON C.ID_VENTA = DV.ID_VENTA
            WHERE C.ID_COMPROBANTE = %s AND C.ESTADO = 'A'
            """
            cursor.execute(sql, (id_comprobante,))
            productos = cursor.fetchall()
            return productos if productos else []
    except pymysql.MySQLError as e:
        print(f"Error en la consulta SQL: {e}")
        return []
    finally:
        conn.close()


def listarTodosDetalleVenta():

    conn = get_db_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = """
            SELECT DV.ID_DETALLE_VENTA,
                   DV.CANTIDAD,
                   DV.SUBTOTAL,
                   P.NOMBRE_PRODUCTO,
                   C.ID_COMPROBANTE,
                   C.ESTADO
            FROM DETALLE_VENTA DV
            INNER JOIN PRODUCTO P ON P.ID_PRODUCTO = DV.ID_PRODUCTO
            INNER JOIN COMPROBANTE C ON C.ID_VENTA = DV.ID_VENTA
            WHERE C.ESTADO = 'A'
            """
            cursor.execute(sql)
            detalles = cursor.fetchall()
            return detalles if detalles else []
    except pymysql.MySQLError as e:
        print(f"Error en la consulta SQL: {e}")
        return []
    finally:
        conn.close()

def dar_baja_comprobante(id_comprobante):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Verificamos si el comprobante existe y está activo (estado 'A')
            sql_comprobante = """
            SELECT ID_COMPROBANTE, ESTADO
            FROM COMPROBANTE
            WHERE ID_COMPROBANTE = %s
            AND ESTADO = 'A'
            """
            cursor.execute(sql_comprobante, (id_comprobante,))
            comprobante = cursor.fetchone()

            if comprobante is None:
                return {"success": False, "message": "Comprobante no encontrado o ya inactivo."}

            # Actualizamos el estado del comprobante a 'I' (Inactivo)
            sql_actualizar_estado = """
            UPDATE COMPROBANTE
            SET ESTADO = 'I'
            WHERE ID_COMPROBANTE = %s
            """
            cursor.execute(sql_actualizar_estado, (id_comprobante,))
            conn.commit()  # Guardamos los cambios

            return {"success": True, "message": "Comprobante dado de baja exitosamente."}

    except pymysql.MySQLError as e:
        print(f"Error en la consulta SQL: {e}")
        return {"success": False, "message": "Ocurrió un error al actualizar el comprobante."}
    finally:
        conn.close()

# Función para eliminar el comprobante
def eliminar_comprobante(id_comprobante):
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            # Verificamos si el comprobante existe y su estado
            sql_check = "SELECT ESTADO FROM COMPROBANTE WHERE ID_COMPROBANTE = %s"
            cursor.execute(sql_check, (id_comprobante,))
            comprobante = cursor.fetchone()

            if not comprobante:
                return False, 'El comprobante no existe.'

            if comprobante['ESTADO'] == 'A':  # Si el estado es "activo", no podemos eliminarlo
                return False, 'El comprobante está activo y no se puede eliminar.'

            # Si el comprobante está inactivo, lo eliminamos
            sql_delete = "DELETE FROM COMPROBANTE WHERE ID_COMPROBANTE = %s"
            cursor.execute(sql_delete, (id_comprobante,))
            conn.commit()

            return True, 'Comprobante eliminado exitosamente.'
    except Exception as e:
        return False, f"Error al eliminar el comprobante: {str(e)}"
    finally:
        if conn:
            conn.close()

def modificar_comprobante(id_comprobante, nuevo_tipo_comprobante):
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            # Verificamos si el comprobante existe y está activo
            sql_check = "SELECT ESTADO FROM COMPROBANTE WHERE ID_COMPROBANTE = %s"
            cursor.execute(sql_check, (id_comprobante,))
            comprobante = cursor.fetchone()

            if not comprobante:
                return False, 'El comprobante no existe.'

            if comprobante['ESTADO'] == 'I':  # Comprobante inactivo
                return False, 'No se puede modificar un comprobante inactivo.'

            # Validamos que el tipo de comprobante sea Boleta o Factura
            if nuevo_tipo_comprobante not in ['B', 'F']:
                return False, 'El tipo de comprobante debe ser "B" (Boleta) o "F" (Factura).'

            # Si el comprobante está activo y el tipo es válido, procedemos con la actualización
            sql_update = """
                UPDATE COMPROBANTE
                SET TIPO_COMPROBANTE = %s
                WHERE ID_COMPROBANTE = %s
            """
            cursor.execute(sql_update, (nuevo_tipo_comprobante, id_comprobante))
            conn.commit()

            return True, 'El tipo de comprobante ha sido actualizado exitosamente.'
    except Exception as e:
        return False, f"Error al modificar el comprobante: {str(e)}"
    finally:
        if conn:
            conn.close()



