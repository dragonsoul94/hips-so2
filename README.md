# HIPS - SO2

HIPS desarrollado con Python y Flask para SO2 - 2021.
Funcionaliades:

- Determinar cambios en los archivos /etc/passwd y /etc/shadow a traves de md5sum.
- Revisar usuarios conectados en el servidor.
- Revisar si el servidor se encuentra en modo promiscuo.
- Determinar errores de autenticacion en el directorio /var/log/secure.
- Determinar errores de acceso indebido desde el servidor web.
- Revisar el directorio /tmp en busca de scripts y shells.
- Revisar errores de ingreso de conexion via SSH.

Como medidas preventivas cuenta con:
- Enviar archivos a cuarentena.
- Bloquear IP's.

Cuando ocurre una alerta o se realiza una medida preventiva se avisa al administrador via email y tambien se registran en los logs *alarmas.log* y *prevencion.log*
## Requerimientos

Para que funcione el HIPS se necesitan de algunas librerias y configuraciones previas.
Este proceso se realizo en una distribucion Linux - CentOS 8.

**Python 3**

En la consola ejecutamos el comando: `sudo yum install python3 -y`

**PIP**

En la consola ejecutamos el comando: `sudo yum install python3-pip -y`

**PostgreSQL**

En la consola ejecutamos los siguientes comandos, en el mismo orden:

`sudo dnf install -y <https://download.postgresql.org/pub/repos/yum/reporpms/EL-8-x86_64/pgdg-redhat-repo-latest.noarch.rpm>`

`sudo dnf -qy module disable postgresql`

`sudo dnf install -y postgresql13-server`

```
sudo /usr/pgsql-13/bin/postgresql-13-setup initdb
sudo systemctl enable postgresql-13
sudo systemctl start postgresql-13
```

**IPTables**

Para instalar: <https://linuxize.com/post/how-to-install-iptables-on-centos-7/>

## Configuracion del entorno virtual

Para este trabajo creamos un entorno virtual en la cual instalamos las librerias Python utilizadas, para hacerlo: <https://www.digitalocean.com/community/tutorials/how-to-install-python-3-and-set-up-a-programming-environment-on-centos-8-es>

## Instalacion librerias Python

Asegurarse de tener activado el entorno virtual, luego para instalar una libreria : `python pip install [libreria]`

**Librerias utilizadas**

Las siguientes librerias necesitan ser instaladas:

- psycopg2
- flask
- flask-login
- sqlalchemy

## Configuracion de la Base de Datos

**Agregar una contrasena al usuario 'Postgres'**

Para esto realizar los siguientes comandos:

`sudo su postgres`

`psql`

`ALTER USER "postgres" WITH password '[constrasena_nueva];`

**Crear base de datos y tablas**

Para que funcione nuestro HIPS la base de datos debe estar configurada de antemano, asi como las tablas, para ello dentro del psql ejecutamos los siguientes comandos:

`CREATE DATABASE hipso2;`

`\c hipso2`

`CREATE TABLE md5sum (file varchar, num_hash varchar);`

`CREATE TABLE login (id integer, username varchar(30), password varchar(30));`

Para crear un usuario se necesita cargar de antemano en la tabla login, para ello:

`INSERT INTO login (id, username, password) VALUES (num_id, 'username', 'password')`

**Configurar pg_hba.conf**

Para que funcione correctamente debemos cambiar el metodo de autenticacion a MD5, para ello ejecutamos los siguientes comandos: 

`sudo su postgres`

`nano /var/lib/pgsql/13/data/pg_hba.conf`

Realizamos los siguientes cambios:
- local all all peer 		-> local all all md5

volvemos a root: `exit` y reiniciamos el servidor de PostgreSQL: `sudo systemctl restart postgresql-13.service`

## Ajustes finales

En la consola, accedemos al entorno y ejecutamos el archivo *pre_config.py*, que contiene configuraciones previas que son necesarias para que funcione el HIPS:

`python pre_config.py`

En el archivo *secret.ini.example* se tiene una plantilla para completar con informacion sensible de la base de datos y del administrador, asegurese de que el archivo se llame *secret.ini* ya que el mismo esta listado en el *.gitignore*

Por ultimo asegurese que estan corriendo los servicios httpd y SSH, en caso de con contar con httpd:

`sudo yum install httpd`

`sudo systemctl start httpd`

`sudo systemctl start ssh`

## Ejecucion

Por ultimo, en la consola, estando dentro del entorno virtual ejecute el programa *server.py* y en el navegador escriba *localhost:5000* y ya encontraria su HIPS funcionando, apareciendo el login.