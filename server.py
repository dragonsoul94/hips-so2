#interfaz web HIPS
#adriram

from email import message
from flask import (
    Flask,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for
)
import flask
from flask.helpers import flash
from flask_sqlalchemy import SQLAlchemy, _SQLAlchemyState
import psycopg2
import os
import subprocess
import configparser
import hips

class User:
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

    def __repr__(self):
        return f'<User: {self.username}>'

app = Flask(__name__)
app.config['SECRET_KEY'] = 'trabajo-practico-de-so2-hips-*'

consult = hips.connect_hipso2(2)
users = []
for x in range(0,len(consult)):
    users.append(User(consult[x][0],consult[x][1], consult[x][2]))
print(users)
@app.before_request
def before_request():
    g.user = None

    if 'user_id' in session:
        user = [x for x in users if x.id == session['user_id']][0]
        g.user = user

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session.pop('user_id', None)

        username = request.form['username']
        password = request.form['password']
        if username == '':
            return redirect(url_for('login'))
        try:
            user = [x for x in users if x.username == username][0]
            if user and user.password == password:
                session['user_id'] = user.id
                return redirect(url_for('index'))
        except:
            redirect(url_for('login'))

    return render_template('login.html')

# Para cargar mi plantilla html
@app.route('/inicio')
def index():
    return render_template('index.html')

@app.route('/check_md5sum/')
def check_md5sum():
    result = hips.check_md5sum_PS()
    print(result)
    return render_template('index.html', message = result)

@app.route('/check_users_login/')
def check_users_login():
    result = hips.check_users_login()
    return render_template('index.html', message = result)

@app.route('/check_promis_mode_apps/')
def check_promis_mode_apps():
    result = hips.check_promis_mode_apps()
    return render_template('index.html', message = result)

@app.route('/check_authentication_logs/')
def check_authentication_logs():
    result = hips.check_authentication_logs()
    return render_template('index.html', message = result)

@app.route('/check_failed_httpd_access/')
def check_failed_httpd_access():
    result = hips.check_failed_httpd_access()
    return render_template('index.html', message = result)

@app.route('/check_tmp/')
def check_tmp():
    result = hips.check_tmp()
    return render_template('index.html', message = result)

@app.route('/check_failed_ssh/')
def check_failed_ssh():
    result = hips.check_failed_ssh()
    return render_template('index.html', message = result)

@app.route('/check_cron/')
def check_cron():
    result = hips.check_cron()
    return render_template('index.html', message = result)

@app.route('/logout/')
def logout():
    session.pop('user_id', None)
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)