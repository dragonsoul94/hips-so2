#interfaz web HIPS
#adriram

from flask import Flask, render_template
import hips

app = Flask(__name__)

# Para cargar mi plantilla html
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/check_md5sum/')
def check_md5sum():
    result = hips.check_md5sum_PS()
    print(result)
    return result


if __name__ == '__main__':
    app.run(debug=True)