#-------------------------------------------------------------------------------
# Name:        RequestGp.py
# Purpose:     Ejecutar una petición a un servicio de geoprocesamiento
#
# Author:      ecetina
#
# Created:     15/08/2024
# Copyright:   (c) esri 2024
# License:     ESRI COLOMBIA - CUCUTA    
#    ___ ____  _____    _    __  __ 
#   |_ _|  _ \| ____|  / \  |  \/  |
#    | || | | |  _|   / _ \ | |\/| |
#    | || |_| | |___ / ___ \| |  | |
#   |___|____/|_____/_/   \_\_|  |_|                               
#-------------------------------------------------------------------------------

from arcgis.gis import GIS
from arcgis.geoprocessing import import_toolbox
from typing import Dict, Any
from utils.request_gp.utils import addMessage, descifrar_datos, obtener_configuracion

import requests

class RequestGp:
    """
    Clase para ejecutar un geoprocesamiento en un servidor de ArcGIS Enterprise 

    Atributos:
    ----------
    configuracion : dict
        Configuración de la clase, viene de archivo de config.yaml
    usuario : str
        Usuario del portal de ArcGIS Enterprise
    password : str
        Contraseña del portal de ArcGIS Enterprise
    gis : GIS
        Conexión al portal de ArcGIS Enterprise
    required_params : list
        Lista de parámetros requeridos para ejecutar el geoprocesamiento
        ["area_interes_shape", "area_interes_coordenadas", "variable_meteorologica"]

    Métodos:
    --------
    validar_parametros(parametros: dict) -> None
        Valida los parámetros del geoprocesamiento
    ejecutar_geoprocesamiento(parametros: dict) -> dict
        Ejecuta un geoprocesamiento
    """
    def __init__(self):
        """
        Constructor de la clase
        """
        addMessage("----Iniciando la clase RequestGp----")
        self.configuracion = obtener_configuracion()
        self.parametros_servicio_obligatorios = self.configuracion["geoprocesamiento"]["parametros_servicio_obligatorios"]
        self.parametros_servicio_opcionales = self.configuracion["geoprocesamiento"]["parametros_servicio_opcionales"]
        self.url_upload = self.configuracion["geoprocesamiento"]["url_upload"]
        self.usuario, self.password = self._descifrar_credenciales()
        self.gis = GIS(self.configuracion["portal"]["url"], self.usuario, self.password)

    def _descifrar_credenciales(self) -> (str, str):
        """
        Descifra las credenciales del portal de ArcGIS Enterprise
        :return: Usuario y contraseña descifrados
        """
        return descifrar_datos(
            self.configuracion["portal"]["usuario"],
            self.configuracion["portal"]["password"],
            self.configuracion["portal"]["fernet_key"]
        )

    def validar_parametros(self, parametros: Dict[str, Any]) -> None:
        """
        Valida los parámetros del geoprocesamiento
        :param parametros: Diccionario con los parámetros del geoprocesamiento
        :raises ValueError: Si algún parámetro es inválido
        """
        addMessage("Validando los parámetros del geoprocesamiento...")
        for param in self.parametros_servicio_obligatorios:
            if param not in parametros:
                raise ValueError(f"El parámetro '{param}' no puede ser nulo")
            if not parametros[param]:
                raise ValueError(f"El parámetro '{param}' no puede estar vacío")
        count = 0
        for param in self.parametros_servicio_opcionales:
            if param in parametros:
                count += 1
        if count == 1:
            addMessage(f"El parámetro '{param}' es opcional y se pasó correctemente")
            return
        elif count == 2:
            raise ValueError(f"incluya solo uno de los parámetros opcionales: {self.parametros_servicio_opcionales}")
        elif count == 0:
            raise ValueError(f"Debe incluir uno de los parámetros opcionales: {self.parametros_servicio_opcionales}")
        addMessage("Parámetros validados correctamente")



    def upload_file(self, file_path):
        try:
            # Abrir el archivo para subirlo
            with open(file_path, 'rb') as file:
                files = {
                    'file': file  # Aquí solo se pasa el objeto de archivo
                }
                
                # Parámetros requeridos por la API
                data = {
                    'f': 'json',
                    'token': self.gis._con.token
                }
                
                # Hacer la petición POST
                response = requests.post(self.url_upload, data=data, files=files)

                # Usar logging para mostrar la información
                addMessage(f"HTTP Status Code: {response.status_code}")
                addMessage(f"Response Text: {response.text}")
                addMessage(f"Response JSON: {response.json()}")
                
                # Verificar el código de respuesta HTTP
                if response.status_code == 200:
                    try:
                        # Intentar procesar la respuesta JSON
                        response_json = response.json()
                        if 'success' in response_json and response_json['success']:
                            addMessage("Archivo subido exitosamente.")
                            itemid_file = {"itemID": response_json['item']['itemID']}
                            return itemid_file
                        else:
                            raise ValueError(f"Error en la subida del archivo: {response_json}")
                    except requests.exceptions.JSONDecodeError:
                        addMessage("La respuesta no es un JSON válido.")
                        addMessage(f"Contenido de la respuesta: {response.text}")
                else:
                    addMessage(f"Error en la petición HTTP: {response.status_code}")
                    addMessage(f"Contenido de la respuesta: {response.text}")
        
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Error al realizar la petición: {e}")
        except FileNotFoundError:
            raise FileNotFoundError(f"Archivo no encontrado: {file_path}")

    def ejecutar_geoprocesamiento(self, parametros: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ejecutar un geoprocesamiento
        :param parametros: Parámetros del geoprocesamiento
        :return: Resultado del geoprocesamiento
        """
        try:
            self.validar_parametros(parametros)
            
            # Validar y obtener parámetros comunes
            variable_meteorologica = parametros.get("variable_meteorologica")
            if not variable_meteorologica:
                raise ValueError("El parámetro 'variable_meteorologica' es obligatorio.")
            
            url_gp = self.configuracion["geoprocesamiento"]["url"]
            toolbox = import_toolbox(url_gp, gis=self.gis)
            
            area_interes_shape = parametros.get("area_interes_shape")
            area_interes_coordenadas = parametros.get("area_interes_coordenadas")
            
            addMessage("Ejecutando el geoprocesamiento...")
            
            # Llamar a la función del toolbox con los parámetros opcionales si están presentes
            if area_interes_shape:
                resultado = toolbox.determinar_estacion_meteorológica(
                    area_interes_shape,
                    None,
                    variable_meteorologica
                )
            elif area_interes_coordenadas:
                resultado = toolbox.determinar_estacion_meteorológica(
                    None,
                    area_interes_coordenadas,
                    variable_meteorologica
                )
            addMessage("----Geoprocesamiento ejecutado correctamente----")
            return resultado
        
        except ValueError as ve:
            addMessage(f"Error en los parámetros: {ve}")
            return {"status": "ERROR", "message": str(ve)}
        except Exception as e:
            addMessage(f"Error al ejecutar el geoprocesamiento: {e}")
            return {"status": "ERROR", "message": str(e)}
        
        except ValueError as e:
            addMessage(f"Error de valor: {e}")
            return {"status": "ERROR", "message": f"Error de valor: {e}"}

if __name__ == "__main__":
    #Ejm de data_request
    # data_dummies = {
    #     "area_interes_shape": "test",
    #     "area_interes_coordenadas": (4.12345,-74.12345),
    #     "variable_meteorologica": "Precipitación"
    # }
    request_gp = RequestGp()
    coordinates = {'latlng': {'lat': 3.9506847954829625, 'lng': -74.03480529785158}, 'layerPoint': {'x': 514.5, 'y': 194.91681477093206}, 'containerPoint': {'x': 514.5, 'y': 194.91681477093206}}
    coordenadas = (coordinates['latlng']['lat'], coordinates['latlng']['lng'])
    data_request = {}
    #data_request["area_interes_coordenadas"] = coordenadas
    data_request["variable_meteorologica"] = "Temperatura del aire"
    itemid_file = request_gp.upload_file(r"C:\Users\ecetina\OneDrive - Esri NOSA\ideam\herramienta_certificaciones_TyC\geoprocessing-service\data\shape_test\pi_test\PI_TAllG.zip")
    data_request["area_interes_shape"] = itemid_file
    addMessage(itemid_file)
    resultado_gp = request_gp.ejecutar_geoprocesamiento(data_request)
    addMessage(resultado_gp)

