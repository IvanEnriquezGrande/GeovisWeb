from flask import (
    Blueprint,
    render_template,
    request,
    current_app,
    flash,
    url_for,
    redirect,
    render_template_string,
)
from werkzeug.utils import secure_filename
import os
from .generador_mapas import GeneradorMapas

views = Blueprint("views", __name__)

archivos = []  # archivos guardados del "submit"
archivo_shp = ""  # nombre del shp
ruta_shp = ""  # ubicación del shp
ruta_templates = ".\\website\\templates"


def borrar_archivos():
    """
    borrar_Archivos elimina archivos de
    la carpeta test1 y vacía la lista de archivos
    """
    global archivos
    for archivo in archivos:
        os.remove(os.path.join(current_app.config["UPLOAD_PATH"], archivo))
    archivos = []


def extensiones_validas(file):
    """
    extensiones_validas revisa si los archivos
    tienen una extensión permitida
    y retorna true si es el caso.
    """
    file = file.upper()
    ext = file.rsplit(".", 1)[1]

    if ext not in current_app.config["ALLOWED_EXTENSIONS"]:
        return False

    return True


def archivos_obligatorios():
    """
    archivos_obligatorios revisa que existan 4 archivos
    con extensiones .shp .ptj .dbf .shx
    entre los archivos guardados en tes1,
    si se cumple retorna una cadena vacía, pero
    en caso contrario retorna una cadena con la extensión faltante.
    """
    extensiones = [archivo.rsplit(".", 1)[1] for archivo in archivos]
    print(extensiones)

    if "shp" not in extensiones:
        return "Se necesita un archivo con extensión .shp"

    elif "shx" not in extensiones:
        return "Se necesita un archivo con extensión .shx"

    elif "dbf" not in extensiones:
        return "Se necesita un archivo con extensión .dbf"

    elif "prj" not in extensiones:
        return "Se necesita un archivo con extensión .prj"

    return ""


@views.route("/")
def home():
    return render_template("index.html")


@views.route("/quienes_somos")
def quienes_somos():
    return render_template("quienes_somos.html")


@views.route("/upload_file", methods=["GET", "POST"])
def upload_file():
    global archivo_shp
    global ruta_shp
    global archivos
    global ruta_templates

    # revisar si existen mapa1.html
    if os.path.exists(os.path.join(ruta_templates, "mapa1.html")):
        os.remove(os.path.join(ruta_templates, "mapa1.html"))

    if request.method == "POST":
        # Obtener archivos que subió el usuario
        f = request.files.getlist("files2")
        for file in f:
            # revisar si no envió nada
            if file.filename == "":
                flash("Ningún archivo seleccionado")
                return redirect(request.url)

            if file and extensiones_validas(file.filename):
                # buscar archivo con extension .shp
                if str(file.filename).endswith(".shp"):
                    archivo_shp = str(file.filename)
                    ruta_shp = os.path.join(
                        current_app.config["UPLOAD_PATH"], archivo_shp
                    )
                # secure_filename previene que el usuario suba un archivo cuyo nombre
                # sea una ruta relativa y sobreescriba un archivo importante
                filename = secure_filename(str(file.filename))
                file.save(os.path.join(current_app.config["UPLOAD_PATH"], filename))
                # guardar archivo en la lista de archivos
                archivos.append(file.filename)
            else:
                print("Archivo no permitido: {}".format(file.filename))

        archivo_faltante = archivos_obligatorios()

        if archivo_faltante != "":
            # Mostrar aviso con la extension faltante
            flash(archivo_faltante)
        else:
            return redirect(url_for("views.crear_mapa_success"))

    return render_template("crear_mapa.html")


@views.route("/crear_mapa_success", methods=["GET", "POST"])
def crear_mapa_success():
    """
    Usar la clase GeneradorMapas
    para crear el mapa y guardarlo en templates
    o mostrar una página de error si la geometria no es válida
    """
    global ruta_templates
    # global mapa
    if request.method == "POST":
        if request.form.get("action1") == "VALUE1":
            print(ruta_shp)
            return redirect(url_for("views.mapa"))

    return render_template("crear_mapa_success.html")


@views.route("/mapa")
def mapa():
    generador = GeneradorMapas()
    print("Obteniendo datos de " + ruta_shp)
    datos = generador.obtener_datos(ruta_shp)
    colores = generador.obtener_nombres_colores()
    estilo_tiles = generador.obtener_estilo_tiles()

    print("Empezando a generar mapa")
    mapa_generado = generador.generar_mapa(datos)
    print("Mapa generado")
    if mapa_generado is not None:
        borrar_archivos()

        print("Dentro del if")

        # generador.guardar_mapa(ruta_templates, "mapa1", mapa)
        mapa_generado.get_root().width = "800px"
        mapa_generado.get_root().height = "600px"
        print("Cambio de dimensiones listo")
        iframe = mapa_generado.get_root()._repr_html_()

        return render_template_string(
            """
                <!DOCTYPE html>
                <html>
                    <head></head>
                    <body>
                        <h1>Using an iframe</h1>
                        {{ iframe|safe }}
                    </body>
                </html>
            """,
            iframe=iframe,
        )
    else:
        return redirect(url_for("views.error_geometria"))


@views.route("/error")
def error_geometria():
    borrar_archivos()
    return render_template("error_geometria.html")
