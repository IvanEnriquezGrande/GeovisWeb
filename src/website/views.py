from flask import (
    Blueprint,
    render_template,
    request,
    current_app,
    flash,
    url_for,
    redirect,
    send_from_directory,
)
from werkzeug.utils import secure_filename
import os
from .generador_mapas import GeneradorMapas
from .utils import (
    borrar_archivos,
    archivos_obligatorios,
    extensiones_validas,
    convertir_mapa_png,
    generar_datos_graficas,
)

views = Blueprint("views", __name__)

archivos = []  # archivos guardados del "submit"
archivo_shp = ""  # nombre del shp
ruta_shp = ""  # ubicación del shp
ruta_templates = ".\\website\\templates"
mapa_final = None
datos_finales = None


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

    # Revisar si hay archivos en current_app.config["UPLOAD_PATH"]
    uploads = os.path.join(current_app.root_path, current_app.config["UPLOAD_PATH"])
    archivos_uploads = os.listdir(uploads)
    if len(archivos_uploads) != 0:
        print("Borrar archivos en uploads/test1")
        print(archivos_uploads)
        for archivo in archivos_uploads:
            os.remove(os.path.join(uploads, archivo))

        # Hay vaciar la lista archivos, caso contrario ocurre un error
        archivos = []

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
                    ruta_shp = os.path.join(uploads, archivo_shp)
                # secure_filename previene que el usuario suba un archivo cuyo nombre
                # sea una ruta relativa y sobreescriba un archivo importante
                filename = secure_filename(str(file.filename))
                file.save(os.path.join(uploads, filename))
                # guardar archivo en la lista de archivos
                archivos.append(file.filename)
            else:
                print("Archivo no permitido: {}".format(file.filename))

        archivo_faltante = archivos_obligatorios(archivos)

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
    global archivos
    global mapa_final
    global datos_finales
    generador = GeneradorMapas()
    print("Obteniendo datos de " + ruta_shp)
    datos = generador.obtener_datos(ruta_shp)
    # colores = generador.obtener_nombres_colores()
    # estilo_tiles = generador.obtener_estilo_tiles()

    print("Empezando a generar mapa")
    mapa_generado = generador.generar_mapa(datos)
    print("Mapa generado")
    if mapa_generado is not None:
        archivos = borrar_archivos(archivos)

        print("Dentro del if")
        mapa_final = mapa_generado
        mapa_generado.get_root().width = "800em"  # "800px"
        mapa_generado.get_root().height = "600em"  # "600px"
        print("Cambio de dimensiones listo")
        iframe = mapa_generado.get_root()._repr_html_()

        datos2 = datos.drop(columns=["geometry"])
        datos_finales = datos2
        datos_tabla = datos2.to_dict(orient="records")
        datos_graficas = generar_datos_graficas(datos2)
        columnas = datos2.columns
        columnas_tabla = [{"id": col.lower(), "name": col} for col in columnas]
        print(datos.drop(columns=["geometry"]).columns)
        print(len(datos_tabla))
        print(columnas_tabla)
        print(datos_graficas)

        return render_template(
            "mapa.html",
            iframe=iframe,
            datos_tabla=datos_tabla,
            columnas_tabla=columnas_tabla,
            datos_graficas=datos_graficas,
        )
    else:
        return redirect(url_for("views.error_geometria"))


@views.route("/error")
def error_geometria():
    global archivos
    archivos = borrar_archivos(archivos)
    return render_template("error_geometria.html")


@views.route("/uploads/<archivo>/<formato>", methods=["GET", "POST"])
def descargar_mapa(archivo, formato):
    global mapa_final
    # secure_filename previene que el usuario suba un archivo cuyo nombre
    # sea una ruta relativa y sobreescriba un archivo importante
    archivo = secure_filename(str(archivo))
    # Agregar carpeta raíz a la ruta de "uploads"
    uploads = os.path.join(current_app.root_path, current_app.config["UPLOAD_PATH"])
    print(uploads)
    print(formato)

    if formato == "html":
        GeneradorMapas.guardar_mapa(uploads, archivo, mapa_final)
        archivo = archivo + ".html"
    elif formato == "png":
        convertir_mapa_png(mapa_final, archivo, uploads)
        archivo = archivo + ".png"
    else:
        print("ERROR: Formato no soportado")

    # Devolver archivo de la ruta uploads
    return send_from_directory(
        directory=uploads, path=archivo, as_attachment=True, download_name=archivo
    )


@views.route("/uploads/<archivo>", methods=["GET", "POST"])
def descargar_reporte(archivo):
    global datos_finales
    # secure_filename previene que el usuario suba un archivo cuyo nombre
    # sea una ruta relativa y sobreescriba un archivo importante
    archivo = secure_filename(str(archivo))
    archivo = archivo + ".xlsx"
    # Agregar carpeta raíz a la ruta de "uploads"
    uploads = os.path.join(current_app.root_path, current_app.config["UPLOAD_PATH"])
    print(uploads)

    datos_finales.to_excel(
        os.path.join(uploads, archivo), sheet_name="Hoja1", index=False
    )

    # Devolver archivo de la ruta uploads
    return send_from_directory(
        directory=uploads, path=archivo, as_attachment=True, download_name=archivo
    )
