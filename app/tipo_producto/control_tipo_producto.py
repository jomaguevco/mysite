from app.bd import get_db_connection

def obtener_tipos(filtro_nombre=None):
    conexion=get_db_connection()
    with conexion.cursor() as cursor:
        try:
            str="""
                select * from TIPO_PRODUCTO tp
            """
            parametro=[]

            if filtro_nombre:
                str+= " where tp.NOMBRE_TIPO_PRODUCTO LIKE %s"
                parametro.append(f"%{filtro_nombre}%")

            cursor.execute(str, tuple(parametro))
            tipos=cursor.fetchall()
            return tipos

        except Exception as e:
            print(f"Error al mostrar los tipos de productos: {e}")
        finally:
            conexion.close()



def obtener_tipos_de_producto():
    conexion=get_db_connection()
    with conexion.cursor() as cursor:
        try:
            str="""
                select * from TIPO_PRODUCTO
            """

            cursor.execute(str,)
            tipos=cursor.fetchall()
            return tipos
        except Exception as e:
            print(f"Error al mostrar los tipos de productos: {e}")
        finally:
            conexion.close()



def obtener_por_id_tipo(id):
    conexion=get_db_connection()
    with conexion.cursor() as cursor:
        try:
            cursor.execute("SELECT * FROM TIPO_PRODUCTO WHERE ID_TIPO_PRODUCTO=%s", (id,))
            tipo=cursor.fetchone()
            return tipo

        except Exception as e:
            print(f"Error al encontrar el tipo de producto: {e}")
            return None
        finally:
            conexion.close()


def insertar_tipo(nombre,estado):
    conexion=get_db_connection()
    with conexion.cursor() as cursor:
        try:
            cursor.execute("INSERT INTO TIPO_PRODUCTO(NOMBRE_TIPO_PRODUCTO,ESTADO) VALUES (%s, %s)",(nombre,estado))
            conexion.commit()
        except Exception as e:
            print(f"Error al insertar el tipo de producto: {e}")
        finally:
            conexion.close()

def actualizar_tipo(id_tipo,nombre,estado):
    conexion=get_db_connection()
    with conexion.cursor() as cursor:
        try:
            cursor.execute("UPDATE TIPO_PRODUCTO SET NOMBRE_TIPO_PRODUCTO =%s, ESTADO=%s WHERE ID_TIPO_PRODUCTO=%s",(nombre,estado,id_tipo))
            conexion.commit()
        except Exception as e:
            conexion.rollback()
            print(f"Error al actualizar el tipo de producto: {e}")
        finally:
            conexion.close()

def verificarExistencia(nombre):
    conexion=get_db_connection()
    with conexion.cursor() as cursor:
        try:
            cursor.execute("SELECT NOMBRE_TIPO_PRODUCTO FROM TIPO_PRODUCTO ")
            nombres=cursor.fetchall()

            nom = [fila[0] for fila in nombres]

            if nombre in nom:
                return True
            else:
                return False
        except Exception as e:
            print(f"Error al verificar la existencia del tipo de producto: {e}")
        finally:
            conexion.close()

def eliminar_tipo(id_producto):
    conexion=get_db_connection()
    with conexion.cursor() as cursor:
        try:
            sql = """
                SELECT ID_TIPO_PRODUCTO FROM DETALLE_TIPO_PRODUCTO
                WHERE ID_TIPO_PRODUCTO = %s
            """
            cursor.execute(sql, (id_producto,))
            tipo = cursor.fetchone()
            if tipo:
                # Si está referenciado, no eliminar
                return False  # El tipo de producto no se puede eliminar

            delete_sql = "DELETE FROM TIPO_PRODUCTO WHERE ID_TIPO_PRODUCTO=%s"
            cursor.execute(delete_sql, (id_producto,))
            conexion.commit()
            return True
        except Exception as e:
            conexion.rollback()
        finally:
            conexion.close()

def dar_de_baja_tipo(id):
    conexion=get_db_connection()
    with conexion.cursor() as cursor:
        try:
            cursor.execute("UPDATE TIPO_PRODUCTO SET ESTADO='I' WHERE ID_TIPO_PRODUCTO=%s",(id,))
            conexion.commit()
        except Exception as e:
            print(f"Error al dar de baja el tipo de producto: {e}")
        finally:
            conexion.close()



def buscar_por_nombre(nombre):
    conexion=get_db_connection()
    with conexion.cursor() as cursor:
        try:
            cursor.execute("select * from TIPO_PRODUCTO WHERE UPPER(NOMBRE_TIPO_PRODUCTO) LIKE UPPER(%s)",(f"%{nombre}%",))
            tipo=cursor.fetchall()
            return tipo
        except Exception as e:
            print(f"Error al encontrar el tipo de producto: {e}")
            return None
        finally:
            conexion.close()


















