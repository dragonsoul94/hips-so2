# archivo para crear la base de datos en postgresql
# donde se almacenaran las sumas de comprobacion md5
import os
import psycopg2
import subprocess

# Nombre:
# Parametros:
# Esta funcion crea la base de datos que necesitamos para almacenar
# algunas informaciones de comprobacion

def create_table_BD():
    # establecemos conexion
    conn = psycopg2.connect(
        database = "hips", user = "postgres", password = "password")
    #conn.autocommit = True

    #creamos onjeto cursor
    curr = conn.cursor()

    # queries para creacion de tablas
    sql = "CREATE TABLE passwd (md5_checksum varchar(32), date varchar(20));"

    #ejecutamos
    curr.execute(sql)
    #print("tabla creada exitosamente")

    #cerramos conexion
    conn.close()

create_table_BD()

def main():
    print("Creando Base de datos:")
    #llamamos a la funcion para crear la base de datos
    print("creando tablas:")
    #llamamos a la funcion que crea las tablas, listamos las tablas creadas
    print("rellenando tablas")
    #funcion para rellenar con datos iniciales, imprime un OK de confirmacion.


if '__main__' == __name__:
  main()