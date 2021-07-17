#!/usr/bin/python


# Trabajo Practico Sistemas Operativos 2 - HIPS
# Autor: Adriram99

#librerias
import os
import subprocess
import posix
import psycopg2
import hashlib
import hips_bd

# Nombre:
# Parametros:
# Esta funcion verifica si hubieron modificaciones de los archivos binarios del sistema 
# y los archivos /etc/passwd y /etc/shadow 
def checkBPSfile():
    # flags para determinar si ya hubo una revision antes
    fbin = 0;
    fpasswd = 0;
    fshadow = 0;
    #control para /etc/passwd
    md5 = os.system("md5sum /etc/passwd")
    print(md5)
    #en esta parte comparamos con el dato registrado en la bd
    #control para /etc/shadow
    md5 = os.system("sudo md5sum /etc/shadow")
    print(md5)
    #comparamos si hay cambios con respecto al ultimo registro en la bd
    

# Funcion principal 
def main():
    #creamos la base de datos ejecutando el archivo .py
  #os.system("python3 hips_bd.py")
  checkBPSfile()


if '__main__' == __name__:
  main()