import os
import zipfile
from datetime import datetime
from arcpy import env, MakeFeatureLayer_management, Describe, Project_management
from arcpy.da import SearchCursor
from arcpy.management import Delete
from arcgis.gis import GIS
from arcgis.features import FeatureLayer, Feature
from utils.request_gp.utils import obtener_configuracion, descifrar_datos, addMessage

class UpdateTable:
    """
    Clase para actualizar una tabla en un servicio de ArcGIS Enterprise
    """
    def __init__(self):
        """
        Constructor de la clase
        """
        try:
            self.configuracion = obtener_configuracion()
            self.url_upload = self.configuracion["geoprocesamiento"]["url_upload"]
            self.usuario, self.password = self._descifrar_credenciales()
            self.gis = GIS(self.configuracion["portal"]["url"], self.usuario, self.password)
            self.url_tabla_registro = self.configuracion["tabla_registro"]["url"]
            self.ruta_shape = None
        except Exception as e:
            print(f"Error al inicializar la clase UpdateTable: {e}")
            raise

    def _descifrar_credenciales(self) -> (str, str):
        """
        Descifra las credenciales del portal de ArcGIS Enterprise
        :return: Usuario y contraseña descifrados
        """
        try:
            return descifrar_datos(
                self.configuracion["portal"]["usuario"],
                self.configuracion["portal"]["password"],
                self.configuracion["portal"]["fernet_key"]
            )
        except Exception as e:
            print(f"Error al descifrar las credenciales: {e}")
            raise

    def validar_sr_wgs84(self) -> bool:
        """
        Valida el sistema de referencia del archivo shape si es wgs84 retorna self.ruta_shape
        si no proyecta a wgs84 y retorna la ruta del shape proyectado

        Returns:
        --------
        bool
            True si el sistema de referencia es WGS 84, False en caso contrario
            Ejemplo: True
        """
        addMessage("Validando el sistema de referencia del shape...")
        fl_shape = MakeFeatureLayer_management(self.ruta_shape, "fl_shape")
        sr = Describe(fl_shape).spatialReference
        if sr.GCSCode == self.configuracion["geoprocesamiento"]["wgs84_spatial_reference_wkid"]:
            return self.ruta_shape
        else:
            addMessage("Proyectando el shape a WGS 84...")
            ruta_shape_proyectado = os.path.join(env.scratchFolder, "shape_proyectado.shp")
            Project_management(fl_shape, ruta_shape_proyectado, self.configuracion["geoprocesamiento"]["wgs84_spatial_reference_wkid"])
            addMessage(f"Shape proyectado a WGS 84: {ruta_shape_proyectado}")
            return ruta_shape_proyectado

    def obtener_coordenadas_zip(self, zip_file):
        """
        Obtiene las coordenadas de un archivo .zip
    
        Parameters:
        -----------
        zip_file : str
            Ruta del archivo .zip
            Ejemplo: 'C:/path/to/file.zip'
    
        Returns:
        --------
        list
            Lista de coordenadas
            Ejemplo: [[-74.03, 4.64], [-74.04, 4.65]]
        """
        try:
            env.overwriteOutput = True
            # Crear un directorio temporal para extraer el archivo .zip
            temp_dir = os.path.join(os.path.dirname(zip_file), 'temp')
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)
    
            # Extraer el archivo .zip
            with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
    
            # Buscar el archivo .shp en el directorio temporal
            self.ruta_shape = None
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    if file.endswith('.shp'):
                        self.ruta_shape = os.path.join(root, file)
                        break
                if self.ruta_shape:
                    break
    
            if not self.ruta_shape:
                raise FileNotFoundError("No se encontró un archivo .shp en el archivo .zip")

            ruta_shape_proyectado = self.validar_sr_wgs84()
            # Leer el archivo shape y obtener las coordenadas
            coordenadas = tuple()
            with SearchCursor(ruta_shape_proyectado, ["SHAPE@XY"]) as cursor:
                coordenadas = tuple((row[0][0], row[0][1]) for row in cursor)
    
            # Limpiar el directorio temporal
            Delete(temp_dir)
    
            return coordenadas
    
        except Exception as e:
            print(f"Error al obtener las coordenadas del archivo .zip: {e}")
            raise

    def actualizar_tabla(self, data_list):
        """
        Actualiza la tabla registro de solicitudes de certificación t y c

        Parameters:
        -----------
        data_list : list
            Lista de diccionarios con los datos a insertar en la tabla
        """
        try:
            # Crear la capa de la tabla
            layer_tabla = FeatureLayer(self.url_tabla_registro, gis=self.gis)

            # Convertir los datos en objetos Feature
            features = [Feature(attributes=item, geometry=item.pop("geometry", None)) for item in data_list]

            # Insertar los datos
            response = layer_tabla.edit_features(adds=features)

            if 'addResults' in response and all(result['success'] for result in response['addResults']):
                print("Los datos se han insertado en la tabla 'metricas_datos_abiertos'")
            else:
                print(f"Error al insertar los datos: {response}")
        except Exception as e:
            print(f"Error al actualizar la tabla: {e}")
            raise

if __name__ == "__main__":
    data_list = [
        {
            "objectid": 1,
            "tpersona_ri": "Persona 1",
            "tdoc_dp": "Documento 1",
            "ndoc_input": "123456789",
            "nombres_input": "Juan",
            "apellidos_in": "Perez",
            "correo_input": "juan.perez@example.com",
            "tel_input": "555-1234",
            "genero_dp": "Masculino",
            "genero_input": "M",
            "grupetn_dp": "Grupo 1",
            "grupetn_input": "Grupo A",
            "infpoblac_dp": "Info 1",
            "discap_dp": "No",
            "discap_input": "N/A",
            "ginteres_dp": "Interes 1",
            "ginteres_input": "Interes A",
            "variable_dp": "Variable 1",
            "tiposerie_dp": "Serie 1",
            "dias_dropdown": "Lunes",
            "meses_dropdown": "Enero",
            "ano_dropdown": "2023",
            "upload_zip_click_info": "Info 1",
            "resultado_status_": "Exitoso",
            "resultado_message_": "Operación completada",
            "output_state": "Estado 1",
            "date_displ": datetime.strptime("2023-01-01T00:00:00", "%Y-%m-%dT%H:%M:%S"),
            "geometry": {
                "x": -74.03, #coordenadas[0][0]
                "y": 4.64, #coordenadas[0][1]
                "spatialReference": {"wkid": 4326}
            }
        }
    ]
    try:
        update_table = UpdateTable()
        coordenadas = update_table.obtener_coordenadas_zip(r"C:\Users\ecetina\OneDrive - Esri NOSA\ideam\herramienta_certificaciones_TyC\geoprocessing-service\data\shape_test\pi_test\PI_TAllG.zip")
        print(coordenadas)
        print(f"longitud: {coordenadas[0][0]}")
        print(f"latitud: {coordenadas[0][1]}")
        update_table.actualizar_tabla(data_list)
    except Exception as e:
        print(f"Error en el proceso de cargue de datos: {e}")