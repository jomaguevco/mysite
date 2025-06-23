import pymysql
from app.bd import get_db_connection


def obtenerTodasVentas():
    conn = get_db_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = "SELECT V.ID_VENTA, U.NOMBRES || ' ' || U.APELLIDO_PAT || ' ' || U.APELLIDO_MAT AS NOMBRE_COMPLETO, V.FECHA_HORA, V.TOTAL FROM VENTA V INNER JOIN USUARIO U ON V.ID_USUARIO = U.ID_USUARIO"
            cursor.execute(sql)
            envios = cursor.fetchall()
            return envios
    finally:
        conn.close()

                                                ##### Métodos API para Venta #####
##Filtrar por ID
def obtenerVentaPorID(id_venta):
    conn = get_db_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = """
                SELECT
                    V.ID_VENTA,
                    U.NOMBRES || ' ' || U.APELLIDO_PAT || ' ' || U.APELLIDO_MAT AS NOMBRE_COMPLETO,
                    V.FECHA_HORA,
                    V.TOTAL
                FROM
                    VENTA V
                INNER JOIN
                    USUARIO U
                ON
                    V.ID_USUARIO = U.ID_USUARIO
                WHERE
                    V.ID_VENTA = %s
            """
            cursor.execute(sql, (id_venta,))
            venta = cursor.fetchone()  # Usamos `fetchone` porque esperamos un solo resultado
            return venta
    finally:
        conn.close()


##Insertar venta
def insertar_venta(id_usuario, id_tarjeta, subtotal):
    conn = get_db_connection()
    try:
        igv = 0.18
        total = subtotal + (subtotal * igv)

        with conn.cursor() as cursor:
            sql = """
            INSERT INTO VENTA (ID_USUARIO, ID_TARJETA, FECHA_HORA, ESTADO, SUBTOTAL, IGV, TOTAL)
                VALUES (%s, %s, NOW(), 'P', %s, %s, %s)
            """
            cursor.execute(sql, (id_usuario, id_tarjeta, subtotal, igv, total))
            conn.commit()

        return True
    except Exception as e:
        print(f"Error al insertar la venta: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


##Modificar venta
def modificar_venta(id_venta, id_usuario, id_tarjeta, subtotal):
    conn = get_db_connection()
    try:
        igv = 0.18
        total = subtotal + (subtotal * igv)

        with conn.cursor() as cursor:
            sql = """
                UPDATE VENTA
                SET
                    ID_USUARIO = %s,
                    ID_TARJETA = %s,
                    FECHA_HORA = NOW(),
                    SUBTOTAL = %s,
                    TOTAL = %s
                WHERE ID_VENTA = %s;
            """
            cursor.execute(sql, (id_usuario, id_tarjeta, subtotal, total, id_venta))
            conn.commit()

        return True
    except Exception as e:
        print(f"Error al modificar la venta: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


##Eliminar venta
def eliminar_venta(id_venta):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                DELETE FROM VENTA
                WHERE ID_VENTA = %s;
            """
            cursor.execute(sql, (id_venta,))
            conn.commit()

        return True
    except Exception as e:
        print(f"Error al eliminar la venta: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


                                                ##########################################
                                                ##### Métodos API para Detalle Venta #####
##Filtrar todos
def obtenerTodosDetalleVenta():
    conn = get_db_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = """
            SELECT DV.*, P.NOMBRE_PRODUCTO FROM DETALLE_VENTA DV inner join PRODUCTO P on DV.ID_PRODUCTO = P.ID_PRODUCTO;
            """
            cursor.execute(sql)
            detalles = cursor.fetchall()
            return detalles if detalles else []
    except pymysql.MySQLError as e:
        print(f"Error en la consulta SQL: {e}")
        return []
    finally:
        conn.close()


##Filtrar por id Venta, Producto y Tipo Producto
def obtenerDetalleFiltrado(id_venta, id_tipo_producto, id_producto):
    conn = get_db_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = """
            SELECT DV.*, P.NOMBRE_PRODUCTO
            FROM DETALLE_VENTA DV
            INNER JOIN PRODUCTO P ON DV.ID_PRODUCTO = P.ID_PRODUCTO
            WHERE DV.ID_VENTA = %s
              AND DV.ID_TIPO_PRODUCTO = %s
              AND DV.ID_PRODUCTO = %s;
            """
            cursor.execute(sql, (id_venta, id_tipo_producto, id_producto))
            detalles = cursor.fetchall()
            return detalles if detalles else []
    except pymysql.MySQLError as e:
        print(f"Error en la consulta SQL: {e}")
        return []
    finally:
        conn.close()


##Insertar detalle
def insertar_detalle(id_venta, id_tipo_producto, id_producto, cantidad, precio):
    conn = get_db_connection()
    try:
        subtotal = cantidad * precio
        igv = 0.18
        total = subtotal + (subtotal * igv)

        with conn.cursor() as cursor:
            sql = """
            INSERT INTO DETALLE_VENTA (ID_VENTA, ID_TIPO_PRODUCTO, ID_PRODUCTO, CANTIDAD, PRECIO, ESTADO, SUBTOTAL, IGV)
            VALUES (%s, %s, %s, %s, %s, 'A', %s, %s);
            """
            cursor.execute(sql, (id_venta, id_tipo_producto, id_producto, cantidad, precio, total, igv))
            conn.commit()

        return True
    except Exception as e:
        print(f"Error al insertar el detalle de venta: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


##Modificar detalle
def actualizarDetalleVenta(id_venta, id_tipo_producto, id_producto, cantidad, precio):
    conn = get_db_connection()
    try:
        subtotal = cantidad * precio
        igv = 0.18
        total = subtotal + (subtotal * igv)

        with conn.cursor() as cursor:
            sql = """
            UPDATE DETALLE_VENTA
            SET
                CANTIDAD = %s,
                PRECIO = %s,
                SUBTOTAL = %s
            WHERE ID_VENTA = %s AND ID_TIPO_PRODUCTO = %s AND ID_PRODUCTO = %s
            """
            cursor.execute(sql, (cantidad, precio, subtotal, id_venta, id_tipo_producto, id_producto))
            conn.commit()

        return True
    except Exception as e:
        print(f"Error al actualizar el detalle de venta: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


##Eliminar detalle
def eliminarDetalleVenta(id_venta, id_tipo_producto, id_producto):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
            DELETE FROM DETALLE_VENTA
            WHERE ID_VENTA = %s AND ID_TIPO_PRODUCTO = %s AND ID_PRODUCTO = %s;
            """
            cursor.execute(sql, (id_venta, id_tipo_producto, id_producto))
            conn.commit()

        return True
    except Exception as e:
        print(f"Error al eliminar el detalle de venta: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()
