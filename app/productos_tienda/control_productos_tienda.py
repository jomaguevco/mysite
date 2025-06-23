from ..bd import obtener_conexion
from app.bd import get_db_connection

def obtener_generos():
    conexion = get_db_connection()
    with conexion.cursor() as cursor:
        cursor.execute("SELECT ID_GENERO, NOMBRE_GENERO FROM GENERO WHERE ESTADO_GENERO = 'A'")
        generos = cursor.fetchall()
    conexion.close()
    return generos

def obtener_descuentos():
    conexion = get_db_connection()
    with conexion.cursor() as cursor:
        cursor.execute("SELECT ID_DESCUENTO, PORCENTAJE FROM DESCUENTO WHERE ESTADO_DSCTO = 'A' AND FECHA_FIN >= CURDATE()")
        descuentos = cursor.fetchall()
    conexion.close()
    return descuentos

#UNICO DE PRODUCTO

def mostrar_productos(filtro_nombre=None):
    """
    Obtiene los productos de la base de datos con un filtro opcional por nombre.
    """
    conexion = get_db_connection()
    try:
        with conexion.cursor() as cursor:
            query = """
                SELECT p.ID_PRODUCTO, p.NOMBRE_PRODUCTO, p.ANIO_LANZAMIENTO, p.DESCRIPCION,
                       p.ESTADO_PRODUCTO, g.NOMBRE_GENERO, des.PORCENTAJE, dtp.ID_TIPO_PRODUCTO
                FROM PRODUCTO p
                INNER JOIN GENERO g ON p.ID_GENERO = g.ID_GENERO
                INNER JOIN DESCUENTO des ON p.ID_DESCUENTO = des.ID_DESCUENTO
                LEFT JOIN DETALLE_TIPO_PRODUCTO dtp ON p.ID_PRODUCTO = dtp.ID_PRODUCTO
                ORDER BY p.ID_PRODUCTO DESC;
            """

            # Filtro por nombre si está presente
            params = []
            if filtro_nombre:
                query += " WHERE p.NOMBRE_PRODUCTO LIKE %s"
                params.append(f"%{filtro_nombre}%")

            # Ejecutar consulta
            cursor.execute(query, tuple(params))
            productos = cursor.fetchall()
            return productos
    except Exception as e:
        print(f"Error al cargar los productos: {e}")
        return []
    finally:
        conexion.close()



def insertar_producto(nombre_producto, anio_lanzamiento, descripcion, estado_producto, id_descuento, id_genero):
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            cursor.execute(
                "INSERT INTO PRODUCTO (NOMBRE_PRODUCTO, ANIO_LANZAMIENTO, DESCRIPCION, ESTADO_PRODUCTO, ID_DESCUENTO, ID_GENERO) "
                "VALUES (%s, %s, %s, %s, %s, %s)",
                (nombre_producto, anio_lanzamiento, descripcion, estado_producto, id_descuento, id_genero)
            )
            conexion.commit()
            return cursor.lastrowid  # Retorna el ID del producto insertado
    except Exception as e:
        conexion.rollback()
        print(f"Error al insertar el producto: {e}")
        raise  # Levantamos la excepción para manejarla en el controlador
    finally:
        conexion.close()

def obtener_producto_por_id(id_producto):
    conexion = get_db_connection()
    try:
        with conexion.cursor() as cursor:
            cursor.execute("""
                SELECT p.ID_PRODUCTO,p.NOMBRE_PRODUCTO,p.ANIO_LANZAMIENTO,p.DESCRIPCION,p.ESTADO_PRODUCTO,p.ID_DESCUENTO,p.ID_GENERO,
                           d.PORCENTAJE,g.NOMBRE_GENERO
                FROM PRODUCTO p inner join GENERO g on g.ID_GENERO=p.ID_GENERO inner join DESCUENTO d on p.ID_DESCUENTO=d.ID_DESCUENTO
                WHERE p.ID_PRODUCTO = %s
            """, (id_producto,))
            producto = cursor.fetchone()
            return producto
    except Exception as e:
        print(f"Error al obtener el producto: {e}")
    finally:
        conexion.close()


def actualizar_producto(id_producto, nombre_producto, anio_lanzamiento, descripcion, estado_producto, id_descuento, id_genero):
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            # Actualizar la tabla PRODUCTO
            cursor.execute(
                "UPDATE PRODUCTO SET NOMBRE_PRODUCTO = %s, ANIO_LANZAMIENTO = %s, DESCRIPCION = %s, ESTADO_PRODUCTO = %s, ID_DESCUENTO = %s, ID_GENERO = %s WHERE ID_PRODUCTO = %s",
                (nombre_producto, anio_lanzamiento, descripcion, estado_producto, id_descuento, id_genero, id_producto)
            )

            conexion.commit()

    finally:
        conexion.close()


def existe_producto(nombre_producto):
    conexion = get_db_connection()
    try:
        with conexion.cursor() as cursor:
            cursor.execute("SELECT * FROM PRODUCTO p WHERE p.NOMBRE_PRODUCTO = %s", (nombre_producto,))
            producto = cursor.fetchone()
            return producto
    except Exception as e:
        print(f"Error al verificar la existencia del producto: {e}")
    finally:
        conexion.close()

def dar_de_baja_producto(id_producto):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute("UPDATE PRODUCTO SET ESTADO_PRODUCTO = 'I' WHERE ID_PRODUCTO = %s", (id_producto,))
    conexion.commit()
    conexion.close()

#----------------------------------------------------------------------------------------------------------------
def obtener_productos2():
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
            SELECT p.ID_PRODUCTO, p.NOMBRE_PRODUCTO, p.ANIO_LANZAMIENTO, p.DESCRIPCION,
                dtp.ESTADO, dtp.PRECIO, dtp.STOCK, dtp.URL_IMG, tp.NOMBRE_TIPO_PRODUCTO, dtp.ID_TIPO_PRODUCTO, g.NOMBRE_GENERO
            FROM PRODUCTO p
            INNER JOIN DETALLE_TIPO_PRODUCTO dtp ON p.ID_PRODUCTO = dtp.ID_PRODUCTO
            INNER JOIN TIPO_PRODUCTO tp ON dtp.ID_TIPO_PRODUCTO = tp.ID_TIPO_PRODUCTO
            INNER JOIN GENERO g ON p.ID_GENERO = g.ID_GENERO
            ORDER BY p.NOMBRE_PRODUCTO
                            """)
            productos = cursor.fetchall()
        return productos
    finally:
        conn.close()

def obtener_tipos_producto2():
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT ID_TIPO_PRODUCTO, NOMBRE_TIPO_PRODUCTO FROM TIPO_PRODUCTO WHERE ESTADO = 'A'")
            tipos_producto = cursor.fetchall()
        return tipos_producto
    finally:
        conn.close()


def obtener_detalle_tipo_producto(idProducto,idTipoPro):
    conexion = get_db_connection()
    try:
        with conexion.cursor() as cursor:
            cursor.execute("SELECT * FROM DETALLE_TIPO_PRODUCTO WHERE ID_TIPO_PRODUCTO = %s AND ID_PRODUCTO = %s",  (idTipoPro, idProducto))
            detalle=cursor.fetchone()
            return detalle
    except Exception as e:
        print(f"Error al obtener el detalle: {e}")
    finally:
        conexion.close()


def verificar_asociacion_detalle_venta(id_tipo_producto, id_producto):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Verificar si el detalle del tipo de producto está asociado a una venta
            cursor.execute(
                "SELECT COUNT(*) FROM DETALLE_VENTA WHERE ID_TIPO_PRODUCTO = %s AND ID_PRODUCTO = %s",
                (id_tipo_producto, id_producto)
            )
            asociacion = cursor.fetchone()[0]
        return asociacion > 0
    finally:
        conn.close()

def eliminar_detalle_tipo_producto(id_tipo_producto, id_producto):
    conexion = get_db_connection()
    try:
        with conexion.cursor() as cursor:
            # Verificar si el registro existe antes de intentar eliminarlo
            cursor.execute(
                "SELECT COUNT(*) FROM DETALLE_TIPO_PRODUCTO WHERE ID_TIPO_PRODUCTO = %s AND ID_PRODUCTO = %s",
                (id_tipo_producto, id_producto)
            )
            existe = cursor.fetchone()[0]

            if existe == 0:
                # No existe el registro a eliminar, podrías manejarlo como un error o un mensaje flash
                print("No se encontró un detalle de tipo de producto con esos IDs.")  # O manejar con flash

            # Si existe, proceder a eliminar
            cursor.execute(
                "DELETE FROM DETALLE_TIPO_PRODUCTO WHERE ID_TIPO_PRODUCTO = %s AND ID_PRODUCTO = %s",
                (id_tipo_producto, id_producto)
            )
            conexion.commit()
    except Exception as e:
        print(f"Error al eliminar detalle de tipo producto: {e}")
        conexion.rollback()
    finally:
        conexion.close()

def insertar_detalle_tipo_producto2(id_tipo_producto, id_producto, stock, precio, url_img):
    conn = get_db_connection()  # Conectar a la base de datos
    try:
        with conn.cursor() as cursor:
            # Consulta SQL para insertar el detalle del tipo de producto
            sql = """
            INSERT INTO DETALLE_TIPO_PRODUCTO (ID_TIPO_PRODUCTO, ID_PRODUCTO, STOCK, PRECIO, ESTADO, URL_IMG)
            VALUES (%s, %s, %s, %s, 'A', %s)
            """
            cursor.execute(sql, (id_tipo_producto, id_producto, stock, precio, url_img))
            conn.commit()  # Confirmar la transacción
    except Exception as e:
        print(f"Error al insertar el detalle del tipo de producto: {e}")
        conn.rollback()  # Deshacer la transacción en caso de error
    finally:
        conn.close()  # Cerrar la conexión a la base de datos



def obtener_productos(nombre_producto=None, filtro_genero=None):
    conexion = obtener_conexion()
    productos = []

    # Consulta básica para obtener productos
    query = """
        SELECT p.ID_PRODUCTO, p.NOMBRE_PRODUCTO, p.ANIO_LANZAMIENTO, p.DESCRIPCION,
        dtp.ESTADO, dtp.PRECIO, dtp.STOCK, dtp.URL_IMG, tp.NOMBRE_TIPO_PRODUCTO, dtp.ID_TIPO_PRODUCTO, g.NOMBRE_GENERO
        FROM PRODUCTO p
        INNER JOIN DETALLE_TIPO_PRODUCTO dtp ON p.ID_PRODUCTO = dtp.ID_PRODUCTO
        INNER JOIN TIPO_PRODUCTO tp ON dtp.ID_TIPO_PRODUCTO = tp.ID_TIPO_PRODUCTO
        INNER JOIN GENERO g ON p.ID_GENERO = g.ID_GENERO
    """

    conditions = []
    params = []

    # Si se especifica un nombre de producto, se agrega a la consulta
    if nombre_producto:
        conditions.append("p.NOMBRE_PRODUCTO LIKE %s")
        params.append(f"%{nombre_producto}%")

    # Si se especifica un filtro de género diferente de 'todos', se agrega a la consulta
    if filtro_genero and filtro_genero != 'todos':
        conditions.append("g.ID_GENERO = %s")
        params.append(filtro_genero)

    # Si se agregaron condiciones de búsqueda, se las incluye en la consulta
    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += " ORDER BY p.ID_PRODUCTO DESC;"  # Orden descendente por ID_PRODUCTO

    with conexion.cursor() as cursor:
        cursor.execute(query, params)
        productos = cursor.fetchall()
    conexion.close()

    return productos


def obtener_tipos_producto():
    conexion = obtener_conexion()
    tipos_producto = []
    with conexion.cursor() as cursor:
        cursor.execute("SELECT ID_TIPO_PRODUCTO, NOMBRE_TIPO_PRODUCTO FROM TIPO_PRODUCTO WHERE ESTADO = 'A'")
        tipos_producto = cursor.fetchall()
    conexion.close()
    return tipos_producto

def listarProductos():
    conexion = obtener_conexion()
    productos = []
    with conexion.cursor() as cursor:
        cursor.execute("select * from PRODUCTO")
        productos = cursor.fetchall()
    conexion.close()
    return productos

def obtener_productos_por_id(id_producto):
    conexion = obtener_conexion()
    productos = None
    try:
        with conexion.cursor() as cursor:
            cursor.execute("SELECT * FROM PRODUCTO WHERE ID_PRODUCTO = %s", (id_producto,))
            productos = cursor.fetchall()
    except Exception as e:
        print(f"Error al obtener producto por ID: {e}")
    finally:
        conexion.close()
    return productos



def insertar_o_actualizar_detalle_tipo_producto(id_tipo_producto, id_producto, stock, precio, url_img):
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            # Verificar si ya existe el detalle
            cursor.execute(
                "SELECT * FROM DETALLE_TIPO_PRODUCTO WHERE ID_TIPO_PRODUCTO = %s AND ID_PRODUCTO = %s",
                (id_tipo_producto, id_producto)
            )
            detalle = cursor.fetchone()

            if detalle:
                # Si existe, actualiza el registro
                cursor.execute(
                    "UPDATE DETALLE_TIPO_PRODUCTO SET STOCK = %s, PRECIO = %s, URL_IMG = %s "
                    "WHERE ID_TIPO_PRODUCTO = %s AND ID_PRODUCTO = %s",
                    (stock, precio, url_img, id_tipo_producto, id_producto)
                )
                cursor.execute(
                    "DELETE FROM DETALLE_TIPO_PRODUCTO WHERE ID_TIPO_PRODUCTO = %s AND ID_PRODUCTO = %s",
                    (id_tipo_producto, id_producto)
                )
            else:
                # Si no existe, inserta un nuevo registro
                cursor.execute(
                    "INSERT INTO DETALLE_TIPO_PRODUCTO (ID_TIPO_PRODUCTO, ID_PRODUCTO, STOCK, PRECIO, ESTADO, URL_IMG) "
                    "VALUES (%s, %s, %s, %s, 'A', %s)",
                    (id_tipo_producto, id_producto, stock, precio, url_img)
                )
            conexion.commit()
    finally:
        conexion.close()

# -------------------------------------
# Nuevas
# -------------------------------------

def actualizar_detalle_tipo_producto(id_tipo_producto, id_producto, stock, precio, url_img, estado):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
            UPDATE DETALLE_TIPO_PRODUCTO
            SET STOCK = %s, PRECIO = %s, URL_IMG = %s, ESTADO = %s
            WHERE ID_TIPO_PRODUCTO = %s AND ID_PRODUCTO = %s
            """
            cursor.execute(sql, (stock, precio, url_img, estado, id_tipo_producto, id_producto))
            conn.commit()
    except Exception as e:
        print(f"Error al actualizar detalle de producto: {e}")
        conn.rollback()
    finally:
        conn.close()

def obtener_detalle_producto(id_producto, id_tipo_producto):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
            SELECT dtp.ID_PRODUCTO, dtp.ID_TIPO_PRODUCTO, dtp.URL_IMG, p.NOMBRE_PRODUCTO, tp.NOMBRE_TIPO_PRODUCTO,
                   dtp.STOCK, dtp.PRECIO, dtp.ESTADO
            FROM DETALLE_TIPO_PRODUCTO dtp
            INNER JOIN PRODUCTO p ON dtp.ID_PRODUCTO = p.ID_PRODUCTO
            INNER JOIN TIPO_PRODUCTO tp ON dtp.ID_TIPO_PRODUCTO = tp.ID_TIPO_PRODUCTO
            WHERE dtp.ID_PRODUCTO = %s AND dtp.ID_TIPO_PRODUCTO = %s
            """
            cursor.execute(sql, (id_producto, id_tipo_producto))
            return cursor.fetchone()
    finally:
        conn.close()


def validar_producto_sin_asociaciones(id_producto):
    conexion = obtener_conexion()
    conteo = 0
    try:
        with conexion.cursor() as cursor:
            query = """
                SELECT COUNT(*)
                FROM DETALLE_TIPO_PRODUCTO
                WHERE ID_PRODUCTO = %s
            """
            cursor.execute(query, (id_producto,))
            conteo = cursor.fetchone()[0]
    except Exception as e:
        print(f"Error al verificar asociaciones: {e}")
    finally:
        conexion.close()
    return conteo == 0


def eliminar_producto(id_producto):
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            query = "DELETE FROM PRODUCTO WHERE ID_PRODUCTO = %s"
            cursor.execute(query, (id_producto,))
            conexion.commit()
    except Exception as e:
        print(f"Error al eliminar producto: {e}")
    finally:
        conexion.close()


def obtener_producto_por_nombre1(nombre_producto):
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            cursor.execute("SELECT * FROM PRODUCTO WHERE LOWER(NOMBRE_PRODUCTO) LIKE LOWER(%s)", (f"%{nombre_producto}%",))
            productos = cursor.fetchall()
        return productos
    except Exception as e:
        print(f"Error al buscar producto: {e}")
        return []
    finally:
        conexion.close()



