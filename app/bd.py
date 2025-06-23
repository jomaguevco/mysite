import pymysql

def obtener_conexion():
    return pymysql.connect(host='localhost',
                           user='root',
                           password='',
                           db='memoriescity$vinilvibes')

# Aliases for obtener_conexion
get_db_connection_seguridad = obtener_conexion
get_db_connection = obtener_conexion