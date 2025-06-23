from app.bd import obtener_conexion

def get_featured_products():
    conn = obtener_conexion()
    try:
        with conn.cursor() as cursor:
            
            sql = """
            SELECT p.ID_PRODUCTO, p.NOMBRE_PRODUCTO, p.DESCRIPCION, 
                   dtp.PRECIO, dtp.URL_IMG
            FROM PRODUCTO p
            JOIN DETALLE_TIPO_PRODUCTO dtp ON p.ID_PRODUCTO = dtp.ID_PRODUCTO
            ORDER BY p.ID_PRODUCTO DESC
            LIMIT 5
            """
            cursor.execute(sql)
            featured_products = cursor.fetchall()
            return featured_products
    finally:
        conn.close()