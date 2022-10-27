from flask import Blueprint, render_template, request, current_app
import os

views = Blueprint("views", __name__)


@views.route('/')
def home():
    return render_template("index.html")

@views.route('/quienes_somos')
def quienes_somos():
    return render_template("quienes_somos.html")

@views.route('/upload_file', methods=["GET", "POST"])
def upload_file():
    if request.method == 'POST':
        f=request.files.getlist("files2")
        for file in f:
            print(file.filename)
            file.save(os.path.join(current_app.config['UPLOAD_PATH'], file.filename))
    return render_template('/crear_mapa.html')