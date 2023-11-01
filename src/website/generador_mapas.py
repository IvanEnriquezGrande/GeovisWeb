"""
El módulo generador mapas provee las clases necesarias
para crear mapas interactivos (folium.Map) a partir de 
archivos shp y todos los archivos complementarios.
"""

from typing import Optional, Union, Any
import geopandas as gpd
import folium
from folium.plugins import GroupedLayerControl


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
        self._estilo_tiles = {
            "Open StreetMap": "OpenStreetMap",
            "Claro": "CartoDB positron",
            "Oscuro": "CartoDB dark_matter",
        }

        self._params_glob = {
            "zoom_inicial": self._zoom_inicial,
            "estilo_tiles": self._estilo_tiles["Claro"],
        }

        self._tipo_geometria = {
            "puntos": "Point",
            "lineas": "LineString",
            "poligonos": "Polygon",
            "multi_poligonos": "MultiPolygon",
        }

        # Parámetros puntos
        self._color = {
            "lightgray": "lightgray",
            "blue": "blue",
            "darkred": "darkred",
            "black": "black",
            "lightred": "lightred",
            "darkgreen": "darkgreen",
            "red": "red",
            "orange": "orange",
            "white": "white",
            "beige": "beige",
            "darkpurple": "darkpurple",
            "darkblue": "darkblue",
            "purple": "purple",
            "cadetblue": "cadetblue",
            "lightgreen": "lightgreen",
            "pink": "pink",
            "gray": "gray",
            "green": "green",
            "lightblue": "lightblue",
        }

        self._params_puntos = {"color": self._color["lightred"]}

        # Parámetros líneas
        self._params_lineas = {
            "color_linea": "#00FF00",  # Puede ser un valor hexadecimal o el nombre de color válido
            "ancho_linea": 3,
        }

        # Parámetros polígonos
        # Puede ser un valor hexadecimal o el nombre de color válido
        self._params_poligonos = {
            "color_relleno": "green",  # "#00FF00",  # hexadecimal
            "color_borde": "green",  # nombre del color
        }

    def obtener_datos(self, ruta: str) -> gpd.GeoDataFrame:
        """
        obtener_datos lee el archivo especificado en
        ruta y devuelve el GeoDataFrame obtenido
        """

        print("Leyendo archivo")
        datos = gpd.read_file(ruta)  # Leer archivo
        datos = datos.to_crs(epsg=self._CRS)  # Convertir datos a CRS 6365

        for col in datos.columns:
            if (
                datos[col].dtype == "object"
            ):  # Verificar si la columna es de tipo string
                datos[col] = datos[col].str.replace(
                    '"', r"\""
                )  # Reemplazar las comillas por su versión escapada
        print("Lectura de archivo finalizada")

        return datos

    @staticmethod
    def generar_mensajes(datos: gpd.GeoDataFrame) -> list[str]:
        """
        generar_mensajes crea una lista de mensajes,
        cada mensaje se compone del contenido de las
        columnas del GeoDataFrame
        """

        # Seleccionar todas las columnas excepto geometry
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
                                            geometría deseado (puntos, línea, polígono)
        len(geometria): Longitud de la lista

        Si todos los elementos de los datos son de un mismo tipo de geometría válido podemos trabajar con ellos.
        "and geometria" es para validar que la lista no sea vacía, a manera de precaución.
        """

        # Geometría de cada registro de datos
        geometria = list(datos.geometry.type)

        if (
            geometria.count(self._tipo_geometria["puntos"]) == len(geometria)
            and geometria
        ):
            geometria_datos = self._tipo_geometria["puntos"]

        elif (
            geometria.count(self._tipo_geometria["lineas"]) == len(geometria)
            and geometria
        ):
            geometria_datos = self._tipo_geometria["lineas"]

        elif (
            geometria.count(self._tipo_geometria["poligonos"])
            + geometria.count(self._tipo_geometria["multi_poligonos"])
            == len(geometria)
            and geometria
        ):
            geometria_datos = self._tipo_geometria["poligonos"]

        else:
            geometria_datos = "GEOMETRIA NO VALIDA"

        return geometria_datos

    @staticmethod
    def crear_mapa_folium(
        self, latitud: float, longitud: float, params_glob: dict
    ) -> folium.Map:
        """
        Crea un folium.Map centrado en la latitud y longitud especificadas
        y con los parámetros globales dados
        """

        mapa = folium.Map(
            location=[latitud, longitud],
            zoom_start=params_glob["zoom_inicial"],
            control_scale=True,
            tiles=None,
        )

        return mapa

    def generar_mapa(
        self,
        datos: gpd.GeoDataFrame,
        params_glob: Optional[Union[dict, None]] = None,
        params_geometria: Optional[Union[dict, None]] = None,
    ) -> Optional[Union[folium.Map, None]]:
        """
        generar_mapa construye un folium.Map a partir de los datos especificados.
        Los parámetros globales (params_glob) indican el aspecto general del mapa, mientras que
        params_geometria dictan las características que deben tener los elementos dibujados sobre
        el mapa (puntos, líneas, polígonos).
        """

        # Geometría de los datos
        geometria = self.determinar_geometria(datos)
        print(geometria)

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
        print("Mensajes generados")

        # Listas Latitud y longitud de los puntos
        latitud = (
            datos["geometry"].to_crs(epsg=self._CRS_METROS).centroid.to_crs(datos.crs).y
        )
        longitud = (
            datos["geometry"].to_crs(epsg=self._CRS_METROS).centroid.to_crs(datos.crs).x
        )

        # Crear mapa
        print("Crear mapa folium")
        mapa = self.crear_mapa_folium(
            self, latitud.mean(), longitud.mean(), params_glob
        )

        # Definir estilo de teselas y agregarlas al objeto mapa.
        t1 = folium.TileLayer(tiles="OpenStreetMap", name="Open Street Map")
        t2 = folium.TileLayer(tiles="CartoDB positron", name="Claro")
        t3 = folium.TileLayer(tiles="CartoDB dark_matter", name="Oscuro")

        t1.add_to(mapa)
        t2.add_to(mapa)
        t3.add_to(mapa)

        print("Dibujar mapa")

        # Grupos que representan los distintos colores de los objetos.
        verde = folium.FeatureGroup(name="Verde", overlay=False)
        azul = folium.FeatureGroup(name="Azul", overlay=False)
        naranja = folium.FeatureGroup(name="Naranja", overlay=False)
        morado = folium.FeatureGroup(name="Morado", overlay=False)
        rojo = folium.FeatureGroup(name="Rojo", overlay=False)

        grupos = {
            "verde": {"capa": verde, "nombre": "Verde", "color": "green"},
            "azul": {"capa": azul, "nombre": "Azul", "color": "blue"},
            "naranja": {"capa": naranja, "nombre": "Naranja", "color": "orange"},
            "morado": {"capa": morado, "nombre": "Morado", "color": "purple"},
            "rojo": {"capa": rojo, "nombre": "Rojo", "color": "red"},
        }
        # Crear y dibujar mapa de acuerdo a la geometría
        if geometria == self._tipo_geometria["puntos"]:
            print("Mapa de puntos")
            # Listas Latitud y longitud de los puntos
            latitud = datos["geometry"].y
            longitud = datos["geometry"].x

            # Dibujar puntos
            for indice in range(len(datos)):
                folium.Marker(
                    [latitud[indice], longitud[indice]],
                    popup=mensajes[indice],
                    icon=folium.Icon(color=grupos["verde"]["color"]),
                ).add_to(grupos["verde"]["capa"])

                folium.Marker(
                    [latitud[indice], longitud[indice]],
                    popup=mensajes[indice],
                    icon=folium.Icon(color=grupos["azul"]["color"]),
                ).add_to(grupos["azul"]["capa"])

                folium.Marker(
                    [latitud[indice], longitud[indice]],
                    popup=mensajes[indice],
                    icon=folium.Icon(color=grupos["naranja"]["color"]),
                ).add_to(grupos["naranja"]["capa"])

                folium.Marker(
                    [latitud[indice], longitud[indice]],
                    popup=mensajes[indice],
                    icon=folium.Icon(color=grupos["morado"]["color"]),
                ).add_to(grupos["morado"]["capa"])

                folium.Marker(
                    [latitud[indice], longitud[indice]],
                    popup=mensajes[indice],
                    icon=folium.Icon(color=grupos["rojo"]["color"]),
                ).add_to(grupos["rojo"]["capa"])

        elif geometria == self._tipo_geometria["lineas"]:
            # Dibujar línea
            print("Mapa de líneas")
            for indice in range(len(datos)):
                # Sin simplificar la representación de cada fila,
                # el mapa podría no visualizarse
                sim_geo = gpd.GeoSeries(datos.loc[indice, "geometry"]).simplify(
                    tolerance=0.001
                )
                geo_js = sim_geo.to_json()
                geo_js = folium.GeoJson(
                    data=geo_js,
                    style_function=lambda x: {
                        "color": grupos["verde"]["color"],
                        "weight": params_geometria["ancho_linea"],
                    },
                )
                folium.Popup(mensajes[indice]).add_to(geo_js)
                geo_js.add_to(grupos["verde"]["capa"])

                geo_js = sim_geo.to_json()
                geo_js = folium.GeoJson(
                    data=geo_js,
                    style_function=lambda x: {
                        "color": grupos["azul"]["color"],
                        "weight": params_geometria["ancho_linea"],
                    },
                )
                folium.Popup(mensajes[indice]).add_to(geo_js)
                geo_js.add_to(grupos["azul"]["capa"])

                geo_js = sim_geo.to_json()
                geo_js = folium.GeoJson(
                    data=geo_js,
                    style_function=lambda x: {
                        "color": grupos["naranja"]["color"],
                        "weight": params_geometria["ancho_linea"],
                    },
                )
                folium.Popup(mensajes[indice]).add_to(geo_js)
                geo_js.add_to(grupos["naranja"]["capa"])

                geo_js = sim_geo.to_json()
                geo_js = folium.GeoJson(
                    data=geo_js,
                    style_function=lambda x: {
                        "color": grupos["morado"]["color"],
                        "weight": params_geometria["ancho_linea"],
                    },
                )
                folium.Popup(mensajes[indice]).add_to(geo_js)
                geo_js.add_to(grupos["morado"]["capa"])

                geo_js = sim_geo.to_json()
                geo_js = folium.GeoJson(
                    data=geo_js,
                    style_function=lambda x: {
                        "color": grupos["rojo"]["color"],
                        "weight": params_geometria["ancho_linea"],
                    },
                )
                folium.Popup(mensajes[indice]).add_to(geo_js)
                geo_js.add_to(grupos["rojo"]["capa"])

        elif geometria == self._tipo_geometria["poligonos"]:
            # Dibujar polígonos
            print("Mapa de polígonos")

            for indice in range(len(datos)):
                # Sin simplificar la representación de cada fila,
                # el mapa podría no visualizarse
                sim_geo = gpd.GeoSeries(datos.loc[indice, "geometry"]).simplify(
                    tolerance=0.001
                )
                geo_js = sim_geo.to_json()
                geo_js = folium.GeoJson(
                    data=geo_js,
                    style_function=lambda x: {
                        "color": grupos["verde"]["color"],
                        "fillColor": grupos["verde"]["color"],
                    },
                )
                folium.Popup(mensajes[indice]).add_to(geo_js)
                geo_js.add_to(grupos["verde"]["capa"])

                geo_js = sim_geo.to_json()
                geo_js = folium.GeoJson(
                    data=geo_js,
                    style_function=lambda x: {
                        "color": grupos["azul"]["color"],
                        "fillColor": grupos["azul"]["color"],
                    },
                )
                folium.Popup(mensajes[indice]).add_to(geo_js)
                geo_js.add_to(grupos["azul"]["capa"])

                geo_js = sim_geo.to_json()
                geo_js = folium.GeoJson(
                    data=geo_js,
                    style_function=lambda x: {
                        "color": grupos["naranja"]["color"],
                        "fillColor": grupos["naranja"]["color"],
                    },
                )
                folium.Popup(mensajes[indice]).add_to(geo_js)
                geo_js.add_to(grupos["naranja"]["capa"])

                geo_js = sim_geo.to_json()
                geo_js = folium.GeoJson(
                    data=geo_js,
                    style_function=lambda x: {
                        "color": grupos["morado"]["color"],
                        "fillColor": grupos["morado"]["color"],
                    },
                )
                folium.Popup(mensajes[indice]).add_to(geo_js)
                geo_js.add_to(grupos["morado"]["capa"])

                geo_js = sim_geo.to_json()
                geo_js = folium.GeoJson(
                    data=geo_js,
                    style_function=lambda x: {
                        "color": grupos["rojo"]["color"],
                        "fillColor": grupos["rojo"]["color"],
                    },
                )
                folium.Popup(mensajes[indice]).add_to(geo_js)
                geo_js.add_to(grupos["rojo"]["capa"])

        else:
            # Aquí podría devolver un error
            mapa = None
            print("No se puede trabajar con ese tipo de geometria")

        if mapa is not None:
            grupos["verde"]["capa"].add_to(mapa)
            grupos["azul"]["capa"].add_to(mapa)
            grupos["naranja"]["capa"].add_to(mapa)
            grupos["morado"]["capa"].add_to(mapa)
            grupos["rojo"]["capa"].add_to(mapa)

            # folium.LayerControl(collapsed=False).add_to(mapa)

            GroupedLayerControl(
                groups={
                    "---ESTILO---": [t1, t2, t3],
                    "---COLORES---": [verde, azul, naranja, morado, rojo],
                },
                collapsed=False,
            ).add_to(mapa)
        return mapa

    @staticmethod
    def guardar_mapa(ruta: str, nombre: str, mapa: folium.Map):
        """
        guardar_mapa almacena el mapa
        generado en la ruta indicada
        """

        mapa.save(f"{ruta}/{nombre}.html")

    @staticmethod
    def obtener_mapa_html(mapa: folium.Map) -> Any:
        """
        obtener_mapa_html retorna el html correspondiente
        al mapa.
        """

        return mapa.get_root()._repr_html_()

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
        parámetros líneas por defecto
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
