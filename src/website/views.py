from importlib.resources import path
from pathlib import Path
from flask import Blueprint, render_template, request, current_app, flash, url_for, redirect
import os

views = Blueprint("views", __name__)

archivos = []
archivo_shp = ""
ruta = "../uploads/test1/"

def allowed_extensions(file):
    file= file.upper()
    ext = file.rsplit(".",1)[1]

    if ext not in current_app.config["ALLOWEWD_EXTENSIONS"]:
        return False

    return True

def archivos_obligatorios():
    extenciones = []
    for archivo in archivos:
        extenciones.append(archivo.rsplit(".",1)[1])
    print(extenciones)
    
    archivos_f = ""
    
    if "shp" not in extenciones:
        archivos_f = "Se necesita un archivo con extension .shp"
    
    elif "shx" not in extenciones:
        archivos_f = "Se necesita un archivo con extension .shx"
    
    elif "dbf" not in extenciones:
        archivos_f = "Se necesita un archivo con extension .dbf"
 
    return archivos_f    
        

@views.route('/')
def home():
    return render_template("index.html")

@views.route('/quienes_somos')
def quienes_somos():
    return render_template("quienes_somos.html")

@views.route('/upload_file', methods=["GET", "POST"])
def upload_file():
    global archivo_shp
    global ruta
    
    if request.method == 'POST':
        f=request.files.getlist("files2")
        for file in f:
            print(file.filename)
            #prueba = str(file.filename)
            if(allowed_extensions(file.filename)):
                if(str(file.filename).rfind(".shp") != -1):
                    archivo_shp = str(file.filename)
                    ruta = ruta + archivo_shp
                    
                file.save(os.path.join(current_app.config['UPLOAD_PATH'], str(file.filename)))
                archivos.append(file.filename)
                
        archivo_faltante = archivos_obligatorios()
        
        if(archivo_faltante != ""):
            flash(archivo_faltante)

        else:
            return redirect(url_for('views.crear_mapa_success'))

    return render_template('/crear_mapa.html')

@views.route('/crear_mapa_success')
def crear_mapa_success():
    return render_template('/crear_mapa_success.html')