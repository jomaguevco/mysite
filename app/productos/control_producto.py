from app.bd import get_db_connection
from flask import request
from decimal import Decimal


def dict_fetchall(cursor):
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]

def dict_fetchone(cursor):
    row = cursor.fetchone()
    if row is None:
        return None
    columns = [col[0] for col in cursor.description]
    return dict(zip(columns, row))

def get_product_details(product_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
            SELECT p.ID_PRODUCTO, p.NOMBRE_PRODUCTO, p.DESCRIPCION, p.ANIO_LANZAMIENTO,
                   p.ID_GENERO, tp.NOMBRE_TIPO_PRODUCTO, g.NOMBRE_GENERO, dtp.PRECIO,
                   dtp.URL_IMG, d.PORCENTAJE, dtp.STOCK, dtp.ID_TIPO_PRODUCTO, p.id_deezer
            FROM PRODUCTO p
            JOIN DETALLE_TIPO_PRODUCTO dtp ON p.ID_PRODUCTO = dtp.ID_PRODUCTO
            JOIN TIPO_PRODUCTO tp ON dtp.ID_TIPO_PRODUCTO = tp.ID_TIPO_PRODUCTO
            JOIN GENERO g ON p.ID_GENERO = g.ID_GENERO
            LEFT JOIN DESCUENTO d ON p.ID_DESCUENTO = d.ID_DESCUENTO
            WHERE p.ID_PRODUCTO = %s
            """
            cursor.execute(sql, (product_id,))
            product = dict_fetchone(cursor)

            if product:
                # Convertir PRECIO y PORCENTAJE a float si son Decimal
                if isinstance(product['PRECIO'], Decimal):
                    product['PRECIO'] = float(product['PRECIO'])
                if product['PORCENTAJE'] is not None and isinstance(product['PORCENTAJE'], Decimal):
                    product['PORCENTAJE'] = float(product['PORCENTAJE'])

                # Get reviews for the product
                sql_reviews = """
                SELECT r.PUNTUACION, r.COMENTARIO, r.FECHA_RESENA,
                       u.NOMBRE_USUARIO
                FROM RESENA r
                JOIN USUARIO u ON r.ID_USUARIO = u.ID_USUARIO
                WHERE r.ID_PRODUCTO = %s AND r.ESTADO = 'A'
                ORDER BY r.FECHA_RESENA DESC
                """
                cursor.execute(sql_reviews, (product_id,))
                reviews = dict_fetchall(cursor)

                product['reviews'] = reviews

            return product
    finally:
        conn.close()



def get_related_products(genre_id, current_product_id, limit=4):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
            SELECT p.ID_PRODUCTO, p.NOMBRE_PRODUCTO, dtp.PRECIO, dtp.URL_IMG
            FROM PRODUCTO p
            JOIN DETALLE_TIPO_PRODUCTO dtp ON p.ID_PRODUCTO = dtp.ID_PRODUCTO
            WHERE p.ID_GENERO = %s AND p.ID_PRODUCTO != %s
            ORDER BY RAND()
            LIMIT %s
            """
            cursor.execute(sql, (genre_id, current_product_id, limit))
            related_products = dict_fetchall(cursor)
            return related_products
    finally:
        conn.close()

def get_featured_products(limit=5):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
            SELECT p.ID_PRODUCTO, p.NOMBRE_PRODUCTO, p.DESCRIPCION, dtp.PRECIO, dtp.URL_IMG
            FROM PRODUCTO p
            JOIN DETALLE_TIPO_PRODUCTO dtp ON p.ID_PRODUCTO = dtp.ID_PRODUCTO
            ORDER BY RAND()
            LIMIT %s
            """
            cursor.execute(sql, (limit,))
            featured_products = dict_fetchall(cursor)
            return featured_products
    finally:
        conn.close()

def get_products(limit=30):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
            SELECT p.ID_PRODUCTO, p.NOMBRE_PRODUCTO, p.DESCRIPCION, dtp.PRECIO, dtp.URL_IMG
            FROM PRODUCTO p
            JOIN DETALLE_TIPO_PRODUCTO dtp ON p.ID_PRODUCTO = dtp.ID_PRODUCTO
            ORDER BY RAND()
            LIMIT %s
            """
            cursor.execute(sql, (limit,))
            featured_products = dict_fetchall(cursor)
            return featured_products
    finally:
        conn.close()

def buscar_por_genero(genero_id=None):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
            SELECT p.ID_PRODUCTO, p.NOMBRE_PRODUCTO, p.DESCRIPCION, dtp.PRECIO, dtp.URL_IMG, g.NOMBRE_GENERO
            FROM PRODUCTO p
            JOIN DETALLE_TIPO_PRODUCTO dtp ON p.ID_PRODUCTO = dtp.ID_PRODUCTO
            JOIN GENERO g ON p.ID_GENERO = g.ID_GENERO
            WHERE %s IS NULL OR p.ID_GENERO = %s
            ORDER BY RAND()
            LIMIT 30
            """
            cursor.execute(sql, (genero_id, genero_id))
            productos = dict_fetchall(cursor)
            return productos
    finally:
        conn.close()
def buscar_generos():
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
            SELECT ID_GENERO, NOMBRE_GENERO
            FROM GENERO
            WHERE ESTADO_GENERO = 'A'
            """
            cursor.execute(sql)
            generos = dict_fetchall(cursor)
            return generos
    finally:
        conn.close()

def buscar_por_nombre(nombre_producto):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Determina el tipo de búsqueda en función de la entrada
            search_pattern = '%' + nombre_producto.lower() + '%'

            # Intenta buscar por cada campo de manera condicional
            sql_name = """
            SELECT P.ID_PRODUCTO, P.NOMBRE_PRODUCTO, P.DESCRIPCION, P.ESTADO_PRODUCTO, D.PORCENTAJE, P.ID_GENERO, G.NOMBRE_GENERO,
                DT.ID_TIPO_PRODUCTO, DT.PRECIO, DT.STOCK, DT.URL_IMG, TP.NOMBRE_TIPO_PRODUCTO
            FROM PRODUCTO P
            JOIN DETALLE_TIPO_PRODUCTO DT ON P.ID_PRODUCTO = DT.ID_PRODUCTO
            JOIN GENERO G ON P.ID_GENERO = G.ID_GENERO
            INNER JOIN TIPO_PRODUCTO TP ON DT.ID_TIPO_PRODUCTO = TP.ID_TIPO_PRODUCTO
            LEFT JOIN DESCUENTO D ON P.ID_DESCUENTO = D.ID_DESCUENTO
            WHERE LOWER(P.NOMBRE_PRODUCTO) LIKE %s AND P.ESTADO_PRODUCTO = 'A';

            """
            cursor.execute(sql_name, (search_pattern,))
            productos_nombre = dict_fetchall(cursor)

            # Si encuentra resultados en nombre, los devuelve de inmediato
            if productos_nombre:
                return productos_nombre

            # Si no encuentra en nombre, busca en descripción
            sql_description = """
            SELECT P.ID_PRODUCTO, P.NOMBRE_PRODUCTO, P.DESCRIPCION, P.ESTADO_PRODUCTO, D.PORCENTAJE, P.ID_GENERO, G.NOMBRE_GENERO,
                DT.ID_TIPO_PRODUCTO, DT.PRECIO, DT.STOCK, DT.URL_IMG, TP.NOMBRE_TIPO_PRODUCTO
            FROM PRODUCTO P
            JOIN DETALLE_TIPO_PRODUCTO DT ON P.ID_PRODUCTO = DT.ID_PRODUCTO
            JOIN GENERO G ON P.ID_GENERO = G.ID_GENERO
            INNER JOIN TIPO_PRODUCTO TP ON DT.ID_TIPO_PRODUCTO = TP.ID_TIPO_PRODUCTO
            LEFT JOIN DESCUENTO D ON P.ID_DESCUENTO = D.ID_DESCUENTO
            WHERE LOWER(P.DESCRIPCION) LIKE %s;
            """
            cursor.execute(sql_description, (search_pattern,))
            productos_descripcion = dict_fetchall(cursor)

            if productos_descripcion:
                return productos_descripcion

            # Si no encuentra en descripción, busca en género
            sql_genre = """
            SELECT P.ID_PRODUCTO, P.NOMBRE_PRODUCTO, P.DESCRIPCION, P.ESTADO_PRODUCTO, D.PORCENTAJE, P.ID_GENERO, G.NOMBRE_GENERO,
                DT.ID_TIPO_PRODUCTO, DT.PRECIO, DT.STOCK, DT.URL_IMG, TP.NOMBRE_TIPO_PRODUCTO
            FROM PRODUCTO P
            JOIN DETALLE_TIPO_PRODUCTO DT ON P.ID_PRODUCTO = DT.ID_PRODUCTO
            JOIN GENERO G ON P.ID_GENERO = G.ID_GENERO
            INNER JOIN TIPO_PRODUCTO TP ON DT.ID_TIPO_PRODUCTO = TP.ID_TIPO_PRODUCTO
            LEFT JOIN DESCUENTO D ON P.ID_DESCUENTO = D.ID_DESCUENTO
            WHERE LOWER(G.NOMBRE_GENERO) LIKE %s;
            """
            cursor.execute(sql_genre, (search_pattern,))
            productos_genero = dict_fetchall(cursor)

            return productos_genero  # Devuelve los resultados de género si los encuentra
    finally:
        conn.close()





def get_products_by_type(product_type, page=1, per_page=12):
    conn = get_db_connection()
    offset = (page - 1) * per_page
    try:
        with conn.cursor() as cursor:
            sql = """
            SELECT p.ID_PRODUCTO, p.NOMBRE_PRODUCTO, p.DESCRIPCION,
                   tp.NOMBRE_TIPO_PRODUCTO, tp.ID_TIPO_PRODUCTO, g.NOMBRE_GENERO, dtp.PRECIO,
                   dtp.URL_IMG, dtp.STOCK, d.PORCENTAJE
            FROM PRODUCTO p
            JOIN DETALLE_TIPO_PRODUCTO dtp ON p.ID_PRODUCTO = dtp.ID_PRODUCTO
            JOIN TIPO_PRODUCTO tp ON dtp.ID_TIPO_PRODUCTO = tp.ID_TIPO_PRODUCTO
            JOIN GENERO g ON p.ID_GENERO = g.ID_GENERO
            LEFT JOIN DESCUENTO d ON p.ID_DESCUENTO = d.ID_DESCUENTO
            WHERE tp.NOMBRE_TIPO_PRODUCTO = %s
            LIMIT %s OFFSET %s
            """
            cursor.execute(sql, (product_type, per_page, offset))
            products = dict_fetchall(cursor)


            return products
    finally:
        conn.close()

def get_product_stock(product_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
            SELECT dtp.STOCK
            FROM DETALLE_TIPO_PRODUCTO dtp
            WHERE dtp.ID_PRODUCTO = %s
            """
            cursor.execute(sql, (product_id,))
            stock = cursor.fetchone()
            if stock:
                return stock['STOCK']
            return None
    finally:
        conn.close()


def get_products_by_filters(tipo_producto, page, genero_id=None, precio_max=500, descuento=None):
    conn = get_db_connection()
    with conn.cursor() as cursor:
        precio_max_str = request.args.get('filtro_precio', '100')

        try:
            precio_max = int(precio_max_str)
        except ValueError:
            precio_max = 100

        sql = """
        SELECT P.ID_PRODUCTO, P.NOMBRE_PRODUCTO, P.DESCRIPCION, P.ESTADO_PRODUCTO, D.PORCENTAJE, P.ID_GENERO, G.NOMBRE_GENERO,
               DT.ID_TIPO_PRODUCTO, DT.PRECIO, DT.STOCK, DT.URL_IMG
        FROM PRODUCTO P
        JOIN DETALLE_TIPO_PRODUCTO DT ON P.ID_PRODUCTO = DT.ID_PRODUCTO
        JOIN GENERO G ON P.ID_GENERO = G.ID_GENERO
        LEFT JOIN DESCUENTO D ON P.ID_DESCUENTO = D.ID_DESCUENTO
        WHERE DT.ID_TIPO_PRODUCTO = %s AND DT.PRECIO <= %s AND P.ESTADO_PRODUCTO = 'A' AND  DT.STOCK > 0
        """
        params = [tipo_producto, precio_max]

        if genero_id and genero_id != '':
            sql += " AND P.ID_GENERO = %s"
            params.append(genero_id)

        if descuento:
            sql += " AND D.PORCENTAJE > 0"

        print("Consulta SQL generada:")
        print(sql)
        print("Parámetros:", params)

        # Ejecutar la consulta SQL con los parámetros
        cursor.execute(sql, params)
        products = dict_fetchall(cursor)

    # Imprimir productos obtenidos para depuración
    print("Productos obtenidos:", products)

    conn.close()  # Cerrar la conexión de la base de datos
    return products

def obtener_todos_los_productos(genero_id=None):
    conn = get_db_connection()
    with conn.cursor() as cursor:
        sql = """
        SELECT P.ID_PRODUCTO, P.NOMBRE_PRODUCTO, P.DESCRIPCION, P.ESTADO_PRODUCTO, D.PORCENTAJE, P.ID_GENERO, G.NOMBRE_GENERO,
               DT.ID_TIPO_PRODUCTO, DT.PRECIO, DT.STOCK, DT.URL_IMG
        FROM PRODUCTO P
        JOIN DETALLE_TIPO_PRODUCTO DT ON P.ID_PRODUCTO = DT.ID_PRODUCTO
        JOIN GENERO G ON P.ID_GENERO = G.ID_GENERO
        LEFT JOIN DESCUENTO D ON P.ID_DESCUENTO = D.ID_DESCUENTO
        WHERE P.ESTADO_PRODUCTO = 'A' AND DT.STOCK > 0
        """
        params = []

        if genero_id and genero_id != '':
            sql += " AND P.ID_GENERO = %s"
            params.append(genero_id)

        print("Consulta SQL generada:")
        print(sql)
        print("Parámetros:", params)

        cursor.execute(sql, params)
        productos = dict_fetchall(cursor)

    print("Productos obtenidos:", productos)

    conn.close()
    return productos
