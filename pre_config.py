# Archivo .py cuya funcion es realizar ajustes previos
# de manera automatica para el funcionamiento del HIPS

import subprocess
import os
import psycopg2
import string
import configparser

# Nombre: create_dir()
# 
# Esta funcion sirve para crear los ficheros necesarios
# 
def create_dir():
    try:
    # fichero /tmp/quarantine
    # este fichero tiene como funcion almacenar los ficheros maliciosos
        os.system('sudo mkdir /tmp/quarantine')
    # fichero /var/logs/hips
    # este fichero tiene como funcion almacenar las alarmas y modulos de prevencion
        os.system('sudo mkdir /var/log/hips')
        os.system('sudo touch /var/log/hips/alarmas.log')
        os.system('sudo touch /var/log/hips/prevencion.log')
    except:
        print("Hubo un error en la creacion de los ficheros")

# Nombre: send_to_db(tp, ts)
#
# Esta funcion tiene como objetivo almacenar en la base de datos los primeros md5sum generados
#
def send_to_db(tp, ts):
    #buscamos las credenciales
    config = configparser.ConfigParser()
    config.read('secret.ini')
    name_db = config['DEFAULT']['DB_NAME']
    usr_db = config['DEFAULT']['DB_USER']
    pass_db = config['DEFAULT']['DB_PASSWORD']
    #establecemos la conexion
    conn = psycopg2.connect(database=name_db, user=usr_db, password=pass_db)

    #creamos el objeto curso para interactuar con la BD
    curr = conn.cursor()

    #escribimos el query de creacion de BD
    sql = "INSERT INTO md5sum (file, num_hash) VALUES ('/etc/passwd','" + tp + "'),('/etc/shadow','" + ts + "');"
    #sql = "select * from md5sum;" 
    print(sql)
    try:
        curr.execute(sql)
        conn.commit()
        print("Carga de datos realizada exitosamente.")
    except psycopg2.Error:
        print("ERROR.")

    #cerramos la conexion
    conn.close()

# Nombre: first_md5sum
#
# Esta funcion tiene como objetivo generar el primer md5sum de los dir /etc/passwd
# y /etc/shadow para que pueda funcionar correctamente el HIPS
def first_md5sum():
    #generamos los md5sum
    p = subprocess.Popen('md5sum /etc/passwd', stdout=subprocess.PIPE, shell=True)
    (out, err) = p.communicate()
    tp = out.decode('utf-8')
    #print(tp)
    tp = tp.split(' ')[0]  #ubicacion del numero hash
    p = subprocess.Popen('sudo md5sum /etc/shadow', stdout=subprocess.PIPE, shell=True)
    (out, err) = p.communicate()
    ts = out.decode('utf-8')
    ts = ts.split(' ')[0]
    #enviamos a la base de datos
    send_to_db(tp, ts)

# Funcion principal
def main():
    create_dir()
    first_md5sum()

if '__main__' == __name__:
  main()