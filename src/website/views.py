from importlib.resources import path
from flask import Blueprint, render_template, request, current_app, flash, url_for, redirect
from werkzeug.utils import secure_filename
import os
from .generador_mapas import GeneradorMapas

views = Blueprint("views", __name__)

archivos = []           #archivos guardados del sumit
archivo_shp = ""        #ruta del shp
ruta_templates = ".\\website\\templates"

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
    
    elif "prj" not in extensiones:
        return "Se necesita un archivo con extension .prj"

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

@views.route('/crear_mapa_success', methods=["GET", "POST"])
def crear_mapa_success():
    if request.method == 'POST':
        if request.form.get('action1') == 'VALUE1':
            print(archivo_shp)
            global ruta_templates
            generador = GeneradorMapas()
            datos = generador.obtener_datos(archivo_shp)
            colores = generador.obtener_nombres_colores()
            estilo_tiles = generador.obtener_estilo_tiles()

            mapa = generador.generar_mapa(datos)
            if mapa != None:
                generador.guardar_mapa(ruta_templates, "mapa1", mapa)
                return redirect(url_for('views.mapa'))
            else:
                #Mensaje de error
                pass
            
    return render_template('/crear_mapa_success.html')         


@views.route('/mapa')
def mapa():
    return render_template('/mapa1.html')