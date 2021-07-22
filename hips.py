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
  #verificamos /etc/passwd
  md5 = subprocess.check_output(["md5sum", "/etc/passwd"])
  print(md5)

# Funcion principal 
def main():
  checkBPSfile()


if '__main__' == __name__:
  main()