"""
El módulo generador mapas provee las clases necesarias
para crear mapas interactivos (folium.Map) a partir de 
archivos shp y todos los archivos complementarios.
"""

from typing import Optional, Union
import geopandas as gpd
import folium


class GeneradorMapas:
    """
    La clase GeneradorMapas tiene como atributos todos
    los valores necesarios para ejecutar la lectura, 
    operación y transformación de archivos SHP para
    convertirlos en un mapa interactivo (folium.Map)
    """

    def __init__(self) -> None:
        # CRS EPSG:6365
        # https://epsg.io/6365
        # Constante
        self._CRS = 6365

        # Para algunos cálculos se requiere específicamente
        # un CRS en metros, el estándar es 4087
        # https://gis.stackexchange.com/questions/372564/userwarning-when-trying-to-get-centroid-from-a-polygon-geopandas
        self._CRS_METROS = 4087

        # Parámetros globales
        self._zoom_inicial = 7

        # Opciones de tiles para mostrar en el mapa
        self._estilo_tiles = {"open_street_map": "OpenStreetMap",
                              "carto_db_light": "CartoDB positron",
                              "carto_db_dark": "CartoDB dark_matter"}

        self._params_glob = {
            "zoom_inicial": self._zoom_inicial,
            "estilo_tiles": self._estilo_tiles["carto_db_light"]
        }

        self._tipo_geometria = {
            "puntos": "Point",
            "lineas": "LineString",
            "poligonos": "Polygon",
            "multi_poligonos": "MultiPolygon"
        }

        # Parámetros puntos
        self._color = {'lightgray': 'lightgray',
                       'blue': 'blue',
                       'darkred': 'darkred',
                       'black': 'black',
                       'lightred': 'lightred',
                       'darkgreen': 'darkgreen',
                       'red': 'red',
                       'orange': 'orange',
                       'white': 'white',
                       'beige': 'beige',
                       'darkpurple': 'darkpurple',
                       'darkblue': 'darkblue',
                       'purple': 'purple',
                       'cadetblue': 'cadetblue',
                       'lightgreen': 'lightgreen',
                       'pink': 'pink',
                       'gray': 'gray',
                       'green': 'green',
                       'lightblue': 'lightblue'}

        self._params_puntos = {"color": self._color["lightred"]}

        # Parámetros líneas
        self._params_lineas = {
            "color_linea": "#00FF00",  # Puede ser un valor hexadecimal o el nombre de color válido
            "ancho_linea": 3
        }

        # Parámetros polígonos
        # Puede ser un valor hexadecimal o el nombre de color válido
        self._params_poligonos = {
            "color_relleno": "#00FF00",  # hexadecimal
            "color_borde": "green"  # nombre del color
        }

    def obtener_datos(self, ruta: str) -> gpd.GeoDataFrame:
        """
        obtener_datos lee el archivo especificado en 
        ruta y devuelve el GeoDataFrame obtenido
        """

        datos = gpd.read_file(ruta)  # Leer archivo
        datos = datos.to_crs(epsg=self._CRS)  # Convertir datos a CRS 6365

        return datos

    def generar_mensajes(self, datos: gpd.GeoDataFrame) -> list[str]:
        """
        generar_mensajes crea una lista de mensajes,
        cada mensaje se compone del contenido de las 
        columnas del GeoDataFrame
        """

        # Seleccionar todas las columnas excepto  geometry
        cols = [col for col in datos.columns if col not in ["geometry"]]
        datos_mensaje = datos[cols]

        # Construir arreglo de mensajes a mostrar
        mensajes = []

        for _, datos_mensaje in datos_mensaje.iterrows():
            mensaje = ""
            for col in cols:
                mensaje += f"{col}: {datos_mensaje[col]}\n"

            mensajes.append(mensaje)

        return mensajes

    def determinar_geometria(self, datos: gpd.GeoDataFrame) -> str:
        """
        determinar_geometria especifica a qué tipo de geometría pertenecen nuestros datos.

        geometria: Lista del tipo de geometría de cada fila de datos
        geometria.count(self._tipo_geometria[]): Cuenta los elementos que son del tipo de 
                                            geometría deseado (puntos, linea, poligono)
        len(geometria): Longitud de la lista

        Si todos los elementos de los datos son de un mismo tipo de geometría válido podemos trabajar con ellos.
        "and geometria" es para validar que la lista no sea vacía, a manera de precaución.
        """

        # Geometría de cada registro de datos
        geometria = list(datos.geometry.type)
        geometria_datos = ""

        if geometria.count(self._tipo_geometria["puntos"]) == len(geometria) and geometria:
            geometria_datos = self._tipo_geometria["puntos"]

        elif geometria.count(self._tipo_geometria["lineas"]) == len(geometria) and geometria:
            geometria_datos = self._tipo_geometria["lineas"]

        elif geometria.count(self._tipo_geometria["poligonos"]) + geometria.count(self._tipo_geometria["multi_poligonos"]) == len(geometria) and geometria:
            geometria_datos = self._tipo_geometria["poligonos"]

        else:
            geometria_datos = "GEOMETRIA NO VALIDA"

        return geometria_datos

    def crear_mapa_folium(self, latitud: float, longitud: float, params_glob: dict) -> folium.Map:
        """
        Crea un folium.Map centrado en la latitud y longitud especificadas 
        y con los parámetros globales dados
        """

        mapa = folium.Map(location=[latitud,
                                    longitud],
                          zoom_start=params_glob["zoom_inicial"], control_scale=True,
                          tiles=params_glob["estilo_tiles"])
        return mapa

    def generar_mapa(self,
                     datos: gpd.GeoDataFrame,
                     params_glob: Optional[Union[dict, None]] = None,
                     params_geometria: Optional[Union[dict, None]] = None) -> Optional[Union[folium.Map, None]]:
        """
        generar_mapa construye un folium.Map a partir de los datos especificados.
        Los parámetros globales (params_glob) indican el aspecto general del mapa, mientras que
        params_geometria dictan las características que deben tener los elementos dibujados sobre
        el mapa (puntos, líneas, polígonos).
        """

        # Geometría de los datos
        geometria = self.determinar_geometria(datos)

        if params_glob is None:
            params_glob = self._params_glob

        if params_geometria is None:
            if geometria == self._tipo_geometria["puntos"]:
                params_geometria = self._params_puntos

            elif geometria == self._tipo_geometria["lineas"]:
                params_geometria = self._params_lineas
            else:
                params_geometria = self._params_poligonos

        # Mensaje a mostrar en el popup del elemento
        mensajes = self.generar_mensajes(datos)

        # Crear y dibujar mapa de acuerdo a la geometría
        if geometria == self._tipo_geometria["puntos"]:
            # Listas Latitud y longitud de los puntos
            latitud = datos["geometry"].y
            longitud = datos["geometry"].x

            # Crear mapa
            mapa = self.crear_mapa_folium(
                latitud.mean(), longitud.mean(), params_glob)

            # Dibujar puntos
            for indice, fila in datos.iterrows():
                folium.Marker([latitud[indice],
                               longitud[indice]],
                              popup=mensajes[indice],
                              icon=folium.Icon(color=params_geometria["color"])
                              ).add_to(mapa)

        elif geometria == self._tipo_geometria["lineas"]:
            # Listas Latitud y longitud de los puntos
            latitud = datos["geometry"].to_crs(
                epsg=self._CRS_METROS).centroid.to_crs(datos.crs).y
            longitud = datos["geometry"].to_crs(
                epsg=self._CRS_METROS).centroid.to_crs(datos.crs).x

            # Crear mapa
            mapa = self.crear_mapa_folium(
                latitud.mean(), longitud.mean(), params_glob)

            # Dibujar línea
            for indice, fila in datos.iterrows():
                # Sin simplificar la representación de cada fila,
                # el mapa podría no visualizarse
                sim_geo = gpd.GeoSeries(
                    fila['geometry']).simplify(tolerance=0.001)
                geo_j = sim_geo.to_json()
                geo_j = folium.GeoJson(data=geo_j,
                                       style_function=lambda x: {"color": params_geometria["color_linea"],
                                                                 "weight": params_geometria["ancho_linea"]})
                folium.Popup(mensajes[indice]).add_to(geo_j)
                geo_j.add_to(mapa)

        elif geometria == self._tipo_geometria["poligonos"]:
            # Listas Latitud y longitud de los puntos
            latitud = datos["geometry"].to_crs(
                epsg=self._CRS_METROS).centroid.to_crs(datos.crs).y
            longitud = datos["geometry"].to_crs(
                epsg=self._CRS_METROS).centroid.to_crs(datos.crs).x

            # Crear mapa
            mapa = self.crear_mapa_folium(
                latitud.mean(), longitud.mean(), params_glob)

            # Dibujar polígonos
            for indice, fila in datos.iterrows():
                # Sin simplificar la representación de cada fila,
                # el mapa podría no visualizarse
                sim_geo = gpd.GeoSeries(
                    fila['geometry']).simplify(tolerance=0.001)
                geo_j = sim_geo.to_json()
                geo_j = folium.GeoJson(data=geo_j,
                                       style_function=lambda x: {"color": params_geometria["color_borde"],
                                                                 "fillColor": params_geometria["color_relleno"]})
                folium.Popup(mensajes[indice]).add_to(geo_j)
                geo_j.add_to(mapa)

        else:
            # Aquí podría devolver un error
            mapa = None
            print("No se puede trabajar con ese tipo de geometria")

        return mapa

    def guardar_mapa(self, ruta: str, nombre: str, mapa: folium.Map):
        """
        guardar_mapa almacena el mapa 
        generado en la ruta indicada
        """

        mapa.save(f"{ruta}/{nombre}.html")

    def obtener_tipos_geometria(self) -> dict:
        """
        obtener_tipos_geometria devuelve las geometrías
        disponibles
        """
        return self._tipo_geometria

    def obtener_params_glob(self) -> dict:
        """
        obtener_params_glob devuelve los
        parámetros globales por defecto
        """
        return self._params_glob

    def obtener_params_puntos(self) -> dict:
        """
        obtener_params_puntos devuelve los
        parámetros puntos por defecto
        """
        return self._params_puntos

    def obtener_params_lineas(self) -> dict:
        """
        obtener_params_lineas devuelve los
        parámetros lineas por defecto
        """
        return self._params_lineas

    def obtener_params_poligonos(self) -> dict:
        """
        obtener_params_poligonos devuelve los
        parámetros poligonos por defecto
        """
        return self._params_poligonos

    def obtener_nombres_colores(self) -> dict:
        """
        obtener_nombres_colores devuelve un diccionario
        con los nombres de los colores disponibles
        """
        return self._color

    def obtener_estilo_tiles(self) -> dict:
        """
        obtener_estilo_tiles devuelve un diccionario con
        los estilos de tiles disponibles para personalizar
        el mapa
        """
        return self._estilo_tiles
