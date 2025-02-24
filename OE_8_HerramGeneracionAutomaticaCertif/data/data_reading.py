# data/data_reading.py
import pandas as pd
import os

def data_locLims():
    # Obtén la ruta del directorio actual (donde está este script)
    current_dir = os.path.dirname(__file__)
    # Construye la ruta completa al archivo
    file_path = os.path.join(current_dir, '..', 'EMCAct_Locat_RefInfo_V2-1.txt')
    # Lee el archivo
    EMCActLims = pd.read_table(file_path, sep=';')
    return EMCActLims

def data_normales():
    # Obtén la ruta del directorio actual (donde está este script)
    current_dir = os.path.dirname(__file__)
    # Construye la ruta completa al archivo
    file_path = os.path.join(current_dir, '..', 'NormClimatolEstándar_PRECIPITACION_9120.xlsx')
    # Lee el archivo
    normales = pd.read_excel(file_path)
    return normales



