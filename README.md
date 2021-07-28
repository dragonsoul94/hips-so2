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

## Requerimientos

Para que funcione el HIPS se necesitan de algunas librerias y configuraciones previas.
Este proceso se realizo en una distribucion Linux - CentOS 8.

**Python 3**

En la consola ejecutamos el comando: 'sudo yum install python3 -y'

**PIP**

En la consola ejecutamos el comando: 'sudo yum install python3-pip -y'

**PostgreSQL**\n

En la consola ejecutamos los siguientes comandos, en el mismo orden:
'sudo dnf install -y <https://download.postgresql.org/pub/repos/yum/reporpms/EL-8-x86_64/pgdg-redhat-repo-latest.noarch.rpm>'

'sudo dnf -qy module disable postgresql'

'sudo dnf install -y postgresql13-server'

'''
sudo /usr/pgsql-13/bin/postgresql-13-setup initdb
sudo systemctl enable postgresql-13
sudo systemctl start postgresql-13
'''
