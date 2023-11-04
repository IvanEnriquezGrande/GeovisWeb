import os
from flask import current_app


def borrar_archivos(archivos: list[str]) -> list[str]:
    """
    borrar_Archivos elimina archivos de
    la carpeta test1 y vacía la lista de archivos
    """
    uploads = os.path.join(current_app.root_path, current_app.config["UPLOAD_PATH"])
    for archivo in archivos:
        os.remove(os.path.join(uploads, archivo))
    return []


def extensiones_validas(file: str) -> bool:
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


def archivos_obligatorios(archivos: list[str]) -> str:
    """
    archivos_obligatorios revisa que existan 4 archivos
    con extensiones .shp .prj .dbf .shx
    entre los archivos guardados en test1,
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
