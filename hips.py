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
  if c == True:
    print("No coinciden")
    log_alarmas("md5sum diferente",'')
    send_mail_alert("md5sum diferente", msg)
  return msg

# Nombre: send_mail_alert()
#   
#   Esta funcion envia los avisos de alertas al administrador del servidor
#   tiene como parametros el asunto (sub) y el detalle de la alerta (textmail)
def send_mail_alert(sub, texmail):
  # Credenciales de correo gmail
  config = configparser.ConfigParser()
  config.read('secret.ini')
  my_mail = config['ADMIN']['ADM_MAIL']
  mail_pass = config['ADMIN']['ADM_PASSWORD']
  email = config['ADMIN']['TO_MAIL']
  # Configuramos servidor de correo
  s = smtplib.SMTP('smtp.gmail.com', 587)
  s.starttls()
  s.login(my_mail,mail_pass)
  #Parametros del mensaje
  msg = MIMEMultipart()
  msg['From'] = my_mail
  msg['To'] = email
  msg['Subject'] = "HIPS ALERT: " + sub
  msg.attach(MIMEText(texmail, 'plain'))
  #Enviar mensaje
  s.send_message(msg)
  del msg
  #cerramos sesion
  s.quit()

# Nombre: check_users_login()
#   
#   Esta funcion revisa los usuarios conectados, junto con sus IPs usando el comando "w"
#
def check_users_login():
  #consultamos con el comando w -i, para que nos muestra las ip si es posible
  p = subprocess.Popen('w -i 2> /dev/null', stdout=subprocess.PIPE, shell=True) #para evitar que nos salte el error just in case
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
#
#
#
def if_promis_mode():
  #revisamos si el servidor esta actualmente en modo promiscuo
  p = subprocess.Popen('ip a show enp0s3 | grep -i promisc', stdout=subprocess.PIPE, shell=True)
  (out, err) = p.communicate()
  promis_on = out.decode('utf-8')
  if promis_on != '':
    # modo promiscuo 
    log_alarmas("NIC en modo promiscuo", '')
    #se informa al admin
    #send_mail_alert("NIC en modo promiscuo", '')

  #revisamos en el directorio /var/log/secure historial de comandos relacionados con el modo promiscuo
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
  if pon != poff and poff < pon:
    #esta en modo promiscuo
    log_alarmas("NIC en modo promiscuo", '')
    #se informa al admin
    #send_mail_alert("NIC en modo promiscuo", '')
  # en teoria no puede comprobar si es que entro usando ifconfig [interface] promisc

# Nombre: promis_apps()
#
#
#
#def promis_apps():


# Nombre: check_promis_mode_apps()
#
#
#
def check_promis_mode_apps():
  #determinamos si el equipo entro en modo promiscuo
  if_promis_mode()
  #promis_apps()

# Nombre: check_authentication_logs()
#
#
#
def check_authentication_logs():
  #revisamos el dir /var/log/secure 
  p = subprocess.Popen('sudo cat /var/log/secure | grep "authentication failure"', stdout=subprocess.PIPE, shell=True)
  (out,err) = p.communicate()
  authf = out.decode('utf-8')
  laf = authf.count('authentication failure')
  i = 0
  while i < laf:
    #se agregar a alarmas.log
    log_alarmas("authentication failure", '')
  #se alerta al admin 
  #send_mail_alert("Error de autenticacion",authf)

# Nombre: check_failed_httpd_access()
#
#
#
def check_failed_httpd_access():
  #extraemos nuestra ip de secret.ini
  config = configparser.ConfigParser()
  config.read('secret.ini')
  ip = config['CONFIG']['MY_IP']
  #revisamos el dir /var/log/httpd/access_log
  #grep -v -> busqueda inversa
  p = subprocess.Popen('sudo cat /var/log/httpd/access_log | grep -v '+ ip + '| grep -v 127.0.0.1 | grep 404 ', stdout=subprocess.PIPE, shell=True)
  (out,err) = p.communicate()
  lip = out.decode('utf-8').splitlines()
  ips = []
  #extraemos las ip encontradas
  for line in lip:
    ips.append(line.split(" ")[0])
  #bloqueamos las ip
  #for i in ips:

# Nombre; check_tmp()
#
#
#
def check_tmp():
  #revisamos si hay shells o scripts en el dir /tmp
  #risk = ['sh', 'py', 'php', 'c', 'cpp', 'perl', 'exe', ]
  cmd = 'find /tmp -type f -name "*.sh" -o -name "*.py" -o -name "*.php" -o -name "*.c" -o -name "*.cpp" -o -name "*.perl" -o -name "*.ruby"'
  p = subprocess.Popen(cmd, stdout=subprocess.PIPE,shell=True)
  (out, err) = p.communicate()
  shfiles = out.decode('utf-8')
  if shfiles != '':
    qshells = []
    #hay posibles archivos de shell
    for line in shfiles.splitlines():
      qshells.append(line)
      #movemos los archivos en el dir /tmp/quarantine
      #quarantine(line)
    #agregramos la alerta en alarms log
    log_alarmas("Shells y scripts encontrados en /tmp",'')
    send_mail_alert("Shells y scripts encontrados en /tmp",shfiles)
    #agregamos las medidas paliativas en prevencion log
    #log_prevencion()
    send_mail_alert("archivos puestos en cuarentena",shfiles)
  #revisamos si hay scripts en dir /tmp
    #print(qshells)

# Nombre: chech_failed_ssh()
#
#
#
def check_failed_ssh():
  
  config = configparser.ConfigParser()
  config.read('secret.ini')
  ip = config['CONFIG']['MY_IP']
  
  p = subprocess.Popen('cat /var/log/secure | grep "ssh" | grep "Failed password" | grep -v "' + ip + '"', stdout=subprocess.PIPE,shell=True)
  (out, err) = p.communicate()
  intruip = out.decode('utf-8')
  lintruip = intruip.splitlines()
  #t = lintruip[0].split(" ")[-4]
  #print(t)
  ipl = []
  fsshaf = 0 #autenthication failure
  fbip = 0 #block de ip
  mailb = ''
  if len(lintruip) != 0:
    #hay failed passwd ssh
    for line in lintruip:
      i = line.split(" ")[-4]
      ipl.append(i) #ip
      #log de alarmas
      fsshaf = 1 
      log_alarmas("Error de autenticacion SSH", i)
    excess = {}
    for i in ipl:
      if i in excess:
        excess[i] += 1
        if excess[i] == 10: #limite para bloquear ip
          fbip = 1
          mailb += i
          #ip_block(i)
          #se agrega al log de prevencion
      else:
        excess[i] = 1
  if fsshaf == 1:
    #send mail
    send_mail_alert("Error de autenticacion SSH", intruip)
  if fbip == 1:
    send_mail_alert("Se bloqueo una o varias IPs", mailb)

# Nombre: quarantine(dir)
#
#
#
def quarantine(direc):
  p = subprocess.Popen('mv ' + direc + '/tmp/quarantine', stdout=subprocess.PIPE,shell=True)
  (out,err) = p.communicate()


# Funcion principal 
def main():
  #check_md5sum_PS()
  #check_users_login()
  #check_promis_mode_apps()
  #check_authentication_logs()
  #check_failed_httpd_access()
  #check_resources()
  #check_tmp()
  check_failed_ssh()

if '__main__' == __name__:
  main()