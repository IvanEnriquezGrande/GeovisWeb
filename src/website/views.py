from importlib.resources import path
from flask import Blueprint, render_template, request, current_app, flash, url_for, redirect
from werkzeug.utils import secure_filename
import os

views = Blueprint("views", __name__)

archivos = []           #archivos guardados del sumit
archivo_shp = ""        #ruta del shp

def allowed_extensions(file):
    file= file.upper()
    ext = file.rsplit(".",1)[1]

    if ext not in current_app.config["ALLOWEWD_EXTENSIONS"]:
        return False

    return True

def archivos_obligatorios():
    extensiones = [archivo.rsplit(".",1)[1] for archivo in archivos]    
    print(extensiones)    
    
    if "shp" not in extensiones:
        return "Se necesita un archivo con extension .shp"
    
    elif "shx" not in extensiones:
        return "Se necesita un archivo con extension .shx"
    
    elif "dbf" not in extensiones:
        return "Se necesita un archivo con extension .dbf"

    return ""
        

@views.route('/')
def home():
    return render_template("index.html")

@views.route('/quienes_somos')
def quienes_somos():
    return render_template("quienes_somos.html")

@views.route('/upload_file', methods=["GET", "POST"])
def upload_file():
    global archivo_shp    
    
    if request.method == 'POST':
        f=request.files.getlist("files2")
        for file in f:                       
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)            
            
            if file and allowed_extensions(file.filename):
                if(str(file.filename).rfind(".shp") != -1):                    
                    archivo_shp = os.path.join(current_app.config['UPLOAD_PATH'], str(file.filename))                        
                # secure_filename previene que el usuario suba un archivo cuyo nombre 
                # sea una ruta relativa y sobreescriba un archivo importante
                filename = secure_filename(str(file.filename))    
                file.save(os.path.join(current_app.config['UPLOAD_PATH'], filename))
                archivos.append(file.filename)
            else:
                print("Archivo no permitido: {}".format(file.filename))
                
        archivo_faltante = archivos_obligatorios()
        
        if(archivo_faltante != ""):
            flash(archivo_faltante)
        else:
            return redirect(url_for('views.crear_mapa_success'))

    return render_template('/crear_mapa.html')

@views.route('/crear_mapa_success')
def crear_mapa_success():
    return render_template('/crear_mapa_success.html')         
