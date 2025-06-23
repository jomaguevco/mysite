from app.bd import get_db_connection
from app.bd_seguridad import get_db_connection_seguridad

def get_user_orders(user_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
            SELECT v.ID_VENTA, v.FECHA_HORA, v.TOTAL, v.ESTADO,
                  COUNT(dv.ID_PRODUCTO) as TOTAL_PRODUCTOS
            FROM VENTA v
            LEFT JOIN DETALLE_VENTA dv ON v.ID_VENTA = dv.ID_VENTA
            WHERE v.ID_USUARIO = %s
            GROUP BY v.ID_VENTA
            ORDER BY v.FECHA_HORA DESC
            """
            cursor.execute(sql, (user_id,))
            orders = cursor.fetchall()
            return orders
    finally:
        conn.close()

def get_user_orders(user_id):
    conn = get_db_connection()
    with conn.cursor() as cursor:
        sql = """
        SELECT
            *
        FROM
            VENTA v
        LEFT JOIN
            DETALLE_VENTA DV ON v.ID_VENTA = DV.ID_VENTA
        LEFT JOIN
            PRODUCTO P ON DV.ID_PRODUCTO = P.ID_PRODUCTO
        LEFT JOIN
            DETALLE_TIPO_PRODUCTO DTP ON DV.ID_TIPO_PRODUCTO = DTP.ID_TIPO_PRODUCTO
                                        AND DV.ID_PRODUCTO = DTP.ID_PRODUCTO
        WHERE
            v.ID_USUARIO = %s
        GROUP BY
            v.ID_VENTA, P.NOMBRE_PRODUCTO, DTP.URL_IMG, DTP.PRECIO, DV.ESTADO
        ORDER BY
            v.FECHA_HORA DESC
        """
        cursor.execute(sql, (user_id,))
        orders = cursor.fetchall()
    conn.close()
    return orders


# -----------------------------------------------------------------------------

def get_user_orders_producto(user_id, venta_id, producto_id):
    conn = get_db_connection()
    with conn.cursor() as cursor:
        # Consulta base con JOIN
        sql = """
        SELECT
                *
            FROM
                VENTA v
            LEFT JOIN
                DETALLE_VENTA dv ON v.ID_VENTA = dv.ID_VENTA
            LEFT JOIN
                PRODUCTO p ON dv.ID_PRODUCTO = p.ID_PRODUCTO
            LEFT JOIN
                DETALLE_TIPO_PRODUCTO dtp ON dv.ID_TIPO_PRODUCTO = dtp.ID_TIPO_PRODUCTO
                              AND dv.ID_PRODUCTO = dtp.ID_PRODUCTO
            LEFT JOIN
                ENVIO e ON v.ID_VENTA = e.ID_VENTA
            WHERE
                v.ID_USUARIO = %s AND v.ID_VENTA = %s AND p.ID_PRODUCTO = %s
            ORDER BY
                v.FECHA_HORA DESC;

        """

        # Ejecutar la consulta con los parámetros
        cursor.execute(sql, (user_id, venta_id, producto_id))
        orders = cursor.fetchone()

    conn.close()
    return orders



# -----------------------------------
# EJEMPLO DE CONSULTA
# -----------------------------------


# SELECT * FROM VENTA v LEFT JOIN DETALLE_VENTA dv ON v.ID_VENTA =
# dv.ID_VENTA LEFT JOIN PRODUCTO p ON dv.ID_PRODUCTO = p.ID_PRODUCTO
# LEFT JOIN DETALLE_TIPO_PRODUCTO dtp ON dv.ID_TIPO_PRODUCTO =
# dtp.ID_TIPO_PRODUCTO AND dv.ID_PRODUCTO = dtp.ID_PRODUCTO WHERE v.ID_USUARIO = 1
# AND v.ID_VENTA = 9 AND p.ID_PRODUCTO = 1 ORDER BY v.FECHA_HORA DESC;


# ----------------------------------------------------------------------------------------


def get_user_comprobante_by_venta(venta_id):
    conn = get_db_connection()
    with conn.cursor() as cursor:
        # Consulta SQL con JOIN entre las tablas relevantes
        sql = """
        SELECT
            C.ID_COMPROBANTE,
            C.FECHA_EMISION,
            C.TIPO_COMPROBANTE,
            C.TOTAL,
            C.SERIE,
            C.CORRELATIVO,
            V.ID_VENTA,
            V.FECHA_HORA,
            U.NOMBRE_USUARIO,
            DV.CANTIDAD,
            DV.PRECIO,
            DV.SUBTOTAL
        FROM
            COMPROBANTE C
        INNER JOIN
            VENTA V ON C.ID_VENTA = V.ID_VENTA
        INNER JOIN
            USUARIO U ON V.ID_USUARIO = U.ID_USUARIO
        INNER JOIN
            DETALLE_VENTA DV ON V.ID_VENTA = DV.ID_VENTA
        INNER JOIN
            PRODUCTO P ON DV.ID_PRODUCTO = P.ID_PRODUCTO
        WHERE
            V.ID_VENTA = %s
        ORDER BY
            C.ID_COMPROBANTE DESC;
        """

        # Ejecutar la consulta con el parámetro venta_id
        cursor.execute(sql, (venta_id,))
        comprobante = cursor.fetchone()

    conn.close()
    return comprobante





def get_user_profile(user_id):
    conn = get_db_connection_seguridad()
    try:
        with conn.cursor() as cursor:
            sql = """
            SELECT *
             FROM USUARIO
            WHERE ID_USUARIO = %s
            """
            cursor.execute(sql, (user_id,))
            profile_tuple = cursor.fetchone()
            if profile_tuple:
                # Convert tuple to dictionary
                columns = [column[0] for column in cursor.description]
                profile = dict(zip(columns, profile_tuple))
                return profile
            return None
    finally:
        conn.close()

def update_user_profile(user_id, form_data):
    conn = get_db_connection_seguridad()
    try:
        with conn.cursor() as cursor:
            sql = """
            UPDATE USUARIO
            SET TELEFONO = %s, DIRECCION = %s, PROVINCIA = %s,
                DISTRITO = %s, CODIGO_POSTAL = %s
            WHERE ID_USUARIO = %s
            """
            cursor.execute(sql, (
                form_data['telefono'],
                form_data['direccion'],
                form_data['provincia'],
                form_data['distrito'],
                form_data['codigo_postal'],
                user_id
            ))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error updating user profile: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()