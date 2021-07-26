#!/usr/bin/python


# Trabajo Practico Sistemas Operativos 2 - HIPS
# Autor: Adriram99

#librerias
import os
import subprocess
import posix
import hashlib
from sys import stdout
import psycopg2
import time
from datetime import datetime
import random
import string
import getpass
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import logging
import time
import configparser

# Nombre: connect_hipsDB()
#   
# Esta funcion sirve para conectarnos en la base de datos del HIPS para consultas varias
# Recibe como parametro la opcion de lo que deseamos consultar
def connect_hipso2(option):
  #buscamos las credenciales
  config = configparser.ConfigParser()
  config.read('secret.ini')
  name_db = config['DEFAULT']['DB_NAME']
  usr_db = config['DEFAULT']['DB_USER']
  pass_db = config['DEFAULT']['DB_PASSWORD']
  #nos conectamos a la base de datos
  conn = psycopg2.connect(database = name_db, user = usr_db, password = pass_db)
  #creamos el objeto cursor para interactuar con la bd
  curr = conn.cursor()
  #realizamos los queries necesarios segun lo que estamos buscando
  if option == 1: #md5sum
    sql = '''SELECT (num_hash) FROM md5sum;'''
    try:
      curr.execute(sql)
      result = curr.fetchall()
      #print(result)
      return result
    except psycopg2.Error:
      print("ERROR.")
  #cerramos la base de datos
  conn.close()

# Nombre: compare_md5sum(md5p, cmd5p, md5s, cmd5s)
# Esta funcion compara los hash almacenados en la BD y los generados en el servidor
# Recibe como parametros los hash almacenados en la BD y los generados en el servidor
#
def compare_md5sum(md5p, cmd5p, md5s, cmd5s):
  c = True
  msg = "no hubo cambios"
  #/etc/passwd
  temp = cmd5p[0]
  print(temp)
  #print(cmd5p)
  if temp != md5p:
    c = False
    msg = "/etc/passwd fue editado, no coinciden las md5sum."
  #/etc/shadow
  temp = cmd5s[0]
  print(temp)
  # print(cmd5s)
  if temp != md5s:
    c = False
    msg = "/etc/shadow fue editado, no coinciden las md5sum."
  return (c,msg)

# Nombre: check_md5sum_PS()
#   
#   Esta funcion revisa si se editaron los dir /etc/passwd y /etc/shadow a traves de md5sum
#
def check_md5sum_PS():
  #p = subprocess.Popen("command", stdout=subprocess.PIPE, shell=True)
  #(out, err) = p.comunicate()
  # calculamos el hash md5 de /etc/passwd
  p = subprocess.Popen('md5sum /etc/passwd', stdout=subprocess.PIPE, shell=True)
  (out,err) = p.communicate()
  # convertimos en formato legible
  md5p = out.decode('utf-8')
  # nos quedamos con la parte correspondiente al numero hash
  md5p = md5p.split(' ')[0]
  # calculamos el hash md5 de /etc/shadow
  p = subprocess.Popen('sudo md5sum /etc/shadow', stdout=subprocess.PIPE, shell=True)
  (out,err) = p.communicate()
  md5s = out.decode('utf-8')
  md5s = md5s.split(' ')[0]
  # consultamos los registros existentes en la base de datos
  consult = connect_hipso2(1)
  # extraemos los datos que necesitamos
  cmd5p = consult[0]
  cmd5s = consult[1]
  #comparamos
  (c, msg) = compare_md5sum(md5p, cmd5p, md5s, cmd5s)
  if c == False:
    print("No coinciden")
    log_alarmas("md5sum diferente",'')
    #send_mail_alert("md5sum diferente", msg)
  return msg

# Nombre: send_mail_alert()
#   
#   Esta funcion envia los avisos de alertas al administrador del servidor
#   tiene como parametros el asunto (sub) y el detalle de la alerta (textmail)
def send_mail_alert(sub, texmail):
  #configuramos los datos del correo
  remitente = 'hipso2@gmail.com'
  destinatario = 'adriram99@gmail.com'
  #generamos el correo
  email = '''From; %s
  To: %s
  Subject: %s
  %s
  ''' % (remitente, destinatario, sub, texmail)
  #creamos un objeto smtp y enviamos
  server = smtplib.SMTP('gmail-smtp-in.l.google.com:25')
  server.starttls()
  server.ehlo("gmail.com")
  server.mail(remitente)
  server.rcpt(destinatario)
  server.data(email)
  server.quit()

# Nombre: check_users_login()
#   
#   Esta funcion revisa los usuarios conectados, junto con sus IPs usando el comando "w"
#
def check_users_login():
  #consultamos con el comando w -i, para que nos muestra las ip si es posible
  p = subprocess.Popen('w -i > /dev/null') #para evitar que nos salte el error just in case
  (out, err) = p.communicate()
  ip_conn = out.decode('utf-8')
  #enviamos al administrador
  send_mail_alert("IP de usuarios conectados", ip_conn)
  #para mostrar en la web
  return ip_conn

# Nombre: alarmas_log(alarm_type, ip_source)
#   
#   Esta funcion agrega en /var/log/hips/alarmas.log las alertas generadas
#   tiene como parametros el tipo de alerta y la ip fuente de la alarma
def log_alarmas(alarm_type, ip_source):
  # en caso de no contar con el ip 
  if ip_source == '':
    ip_source = 'NULL'
  # anadimos fecha en formato DD/MM/AAAA
  daytime = datetime.now().strftime("%Y/%m/%d, %H:%M:%S")
  print(daytime)
  alarm = daytime + "::" + alarm_type + "::" + ip_source
  print(alarm)
  #os.system("echo " + alarm + " >> /var/log/hips/alarmas.log")
  subprocess.Popen("sudo bash -c 'echo " + alarm + " >> /var/log/hips/alarmas.log'", stdout=subprocess.PIPE, shell=True)

# Nombre: log_prevencion(alarm_type, action)
#   
#   Esta funcion agrega en /var/log/hips/prevencion.log
#   tiene como parametros el tipo de alerta y la ip fuente de la alarma
#def log_prevencion(alarm_type, action):

# Nombre: if_promis_mode()
def if_promis_mode():
  # #revisamos si el servidor esta actualmente en modo promiscuo
  # p = subprocess.Popen('ip a show enp0s3 | grep -i promisc', stdout=subprocess.PIPE, shell=True)
  # (out, err) = p.communicate()
  # promis_on = out.decode('utf-8')
  # #revisamos en el directorio /var/log/secure historial de comandos relacionados con el modo promiscuo
  #para ip link set [interface] promisc on/off
  p = subprocess.Popen('sudo cat /var/log/secure | grep "ip link set" | grep "promisc on"', stdout=subprocess.PIPE, shell=True)
  (out, err) = p.communicate()
  ptemp1 = out.decode('utf-8')
  p = subprocess.Popen('sudo cat /var/log/secure | grep "ip link set" | grep "promisc off"', stdout=subprocess.PIPE, shell=True)
  (out, err) = p.communicate()
  ptemp2 = out.decode('utf-8')
  #convertimos en listas
  lon = ptemp1.splitlines()
  loff = ptemp2.splitlines()
  pon = len(lon)
  poff = len(loff)
  if pon != poff:
    #esta en modo promiscuo
    log_alarmas("NIC en modo promiscuo", '')
    #se informa al admin
    send_mail_alert("NIC en modo promiscuo", '')
  #para ifconfig [interface] promisc
  # p = subprocess.Popen('sudo cat /var/log/secure | grep "ifconfig" | grep "promisc"', stdout=subprocess.PIPE, shell=True)
  # (out, err) = p.communicate()
  # ptemp3 = out.decode('utf-8')
  # lifc = ptemp3.splitlines()
  # pifc = len(lifc)
  # if pifc%2 != 0

# Nombre: promis_apps()
#def promis_apps():


# Nombre: check_promis_mode_apps()
#
#
#
def check_promis_mode_apps():
  #determinamos si el equipo entro en modo promiscuo
  if_promis_mode()
  #promis_apps()
# Funcion principal 
def main():
  check_md5sum_PS()
#   check_users_login()
#   check_promis_mode()


if '__main__' == __name__:
  main()