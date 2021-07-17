# archivo para crear la base de datos en postgresql
# donde se almacenaran las sumas de comprobacion md5
import os
import psycopg2
import subprocess

# Nombre:
# Parametros:
# Esta funcion crea la base de datos que necesitamos para almacenar
# algunas informaciones de comprobacion
def createBD():
    # establecemos la conexion
    try:
        connect = psycopg2.connect(database = "postgres", user = "postgres", password = " ")
    except psycopg2.Error as e:
        print('error')
    #connect.autocommit = True

    # creamos el objeto cursor
    curr = connect.cursor()

    # query para crear nueva base de datos
    sql = "CREATE database hips;"

    #creamos la BD
    curr.execute(sql)
    print("BD creado exitosamente")

    #cerramos la conexion
    connect.close()

def create_table_BD():
    # establecemos conexion
    conn = psycopg2.connect(
        database = "hips", user = "postgres", password = " ")
    #conn.autocommit = True

    #creamos onjeto cursor
    curr = conn.cursor()

    # queries para creacion de tablas
    sql = "CREATE TABLE passwd (md5_checksum varchar(32), date varchar(20); )"

    #ejecutamos
    curr.execute(sql)
    print("tabla creada exitosamente")

    #cerramos conexion
    conn.close()