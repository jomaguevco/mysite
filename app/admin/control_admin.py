from app.bd import get_db_connection

def get_all_products():
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
            SELECT p.ID_PRODUCTO, p.NOMBRE_PRODUCTO, p.DESCRIPCION,
                   tp.NOMBRE_TIPO_PRODUCTO, g.NOMBRE_GENERO, dtp.PRECIO,
                   dtp.STOCK, dtp.URL_IMG
            FROM PRODUCTO p
            JOIN DETALLE_TIPO_PRODUCTO dtp ON p.ID_PRODUCTO = dtp.ID_PRODUCTO
            JOIN TIPO_PRODUCTO tp ON dtp.ID_TIPO_PRODUCTO = tp.ID_TIPO_PRODUCTO
            JOIN GENERO g ON p.ID_GENERO = g.ID_GENERO
            """
            cursor.execute(sql)
            products = cursor.fetchall()
            return products
    finally:
        conn.close()

def get_product(product_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
            SELECT p.ID_PRODUCTO, p.NOMBRE_PRODUCTO, p.DESCRIPCION, p.ANIO_LANZAMIENTO,
                   p.ID_GENERO, tp.ID_TIPO_PRODUCTO, dtp.PRECIO, dtp.STOCK, dtp.URL_IMG
            FROM PRODUCTO p
            JOIN DETALLE_TIPO_PRODUCTO dtp ON p.ID_PRODUCTO = dtp.ID_PRODUCTO
            JOIN TIPO_PRODUCTO tp ON dtp.ID_TIPO_PRODUCTO = tp.ID_TIPO_PRODUCTO
            WHERE p.ID_PRODUCTO = %s
            """
            cursor.execute(sql, (product_id,))
            product = cursor.fetchone()
            return product
    finally:
        conn.close()

def update_product(product_id, form_data):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql_product = """
            UPDATE PRODUCTO
            SET NOMBRE_PRODUCTO = %s, DESCRIPCION = %s, ANIO_LANZAMIENTO = %s, ID_GENERO = %s
            WHERE ID_PRODUCTO = %s
            """
            cursor.execute(sql_product, (
                form_data['nombre_producto'],
                form_data['descripcion'],
                form_data['anio_lanzamiento'],
                form_data['id_genero'],
                product_id
            ))

            sql_detalle = """
            UPDATE DETALLE_TIPO_PRODUCTO
            SET PRECIO = %s, STOCK = %s, URL_IMG = %s
            WHERE ID_PRODUCTO = %s AND ID_TIPO_PRODUCTO = %s
            """
            cursor.execute(sql_detalle, (
                form_data['precio'],
                form_data['stock'],
                form_data['url_img'],
                product_id,
                form_data['id_tipo_producto']
            ))

        conn.commit()
        return True
    except Exception as e:
        print(f"Error updating product: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def delete_product(product_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql_detalle = "DELETE FROM DETALLE_TIPO_PRODUCTO WHERE ID_PRODUCTO = %s"
            cursor.execute(sql_detalle, (product_id,))

            sql_product = "DELETE FROM PRODUCTO WHERE ID_PRODUCTO = %s"
            cursor.execute(sql_product, (product_id,))

        conn.commit()
        return True
    except Exception as e:
        print(f"Error deleting product: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


