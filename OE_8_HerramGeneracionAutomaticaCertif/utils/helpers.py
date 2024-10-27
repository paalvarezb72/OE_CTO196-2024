# utils/helpers.py
import pandas as pd
import numpy as np
import re
import pythoncom
import time
import io
import os
import data.derivadasclc as dvd
from datetime import datetime
from docx import Document
from utils.db_connection import create_connection
from data.data_reading import data_normales
from docx2pdf import convert

def obtener_sensor(selected_variable):
    # Diccionario que mapea prefijos de variables a códigos de sensor
    prefijo_a_sensor = {
        "Precipitación": 'PTPM_CON',
        "Temperatura máxima": 'TMX_CON',
        "Temperatura mínima": 'TMN_CON',
        "Temperatura del aire": 'TSSM_CON',
        "Velocidad del viento": 'VVAG_CON'
    }

    # Itera sobre los prefijos en el diccionario
    for prefijo, sensor in prefijo_a_sensor.items():
        if selected_variable.startswith(prefijo):
            return sensor

    # Retorna None o un valor por defecto si no se encuentra un prefijo correspondiente
    return None

def construir_rango_fechas(dias, meses, ano):
    meses_dict = {"enero": 1, "febrero": 2, "marzo": 3, "abril": 4, "mayo": 5, "junio": 6,
                  "julio": 7, "agosto": 8, "septiembre": 9, "octubre": 10, "noviembre": 11, "diciembre": 12}
    
    # Si días es None o vacío, usar 1 por defecto
    dias = list(map(int, dias)) if dias else [1, 1]

    # Si meses es None o vacío, usar 1 por defecto
    meses = list(map(lambda mes: meses_dict[mes], meses)) if meses else [1, 12]
    
    # Se verifica que el año esté presente
    if not ano:
        raise ValueError("El año es un campo obligatorio")

    ano = list(map(int, ano))

    # Construir la fecha de inicio y fin según los valores disponibles
    fecha_inicio = datetime(ano[0], meses[0], dias[0]).strftime('%Y-%m-%d %H:%M:%S')
    fecha_fin = datetime(ano[-1], meses[-1], dias[-1]).strftime('%Y-%m-%d %H:%M:%S')
    return fecha_inicio, fecha_fin

def construir_codestacion(estacion_seleccionada):
    # Se construye código estación según se solicita en Cassandra
    cod_est = str(estacion_seleccionada['CODIGO'])
    if len(cod_est) == 8:
        # Agregar dos ceros a la izquierda si el código tiene 8 dígitos
        codigo_cass = cod_est.zfill(10)
    elif len(cod_est) == 10:
        # Dejar el código tal cual si tiene 10 dígitos
        codigo_cass = cod_est
    else:
        # Manejar otros casos según sea necesario
        codigo_cass = "Código no válido"

    return codigo_cass

def construir_descripsolicit(var_periodo):
    descripcion = "Solicitud series temporales de " + var_periodo
    return descripcion

def fetch_station_data(cur, inicio, fin, sensor, codestacion):
    query = f'''
    select lm.station, s.name, lm.sensor, lm.event_time + interval '5' hour event_time, lm.event_value 
    from cassandra.raw.weather_events AS lm INNER JOIN cassandra.raw.stations AS s
        ON lm.station = s.stationid
    where lm.station in ('{codestacion}')
    AND lm.event_time BETWEEN timestamp '{inicio}' AND timestamp '{fin}' 
    AND lm.sensor in ('{sensor}')
    '''
    cur.execute(query)
    sttndata = cur.fetchall()

    # Se genera un Data Frame a partir de los datos extraídos
    stationdf = pd.DataFrame(sttndata, columns=['Station', 'Name', 'Sensor', 'Fecha', 'Valor'])

    return stationdf[['Fecha', 'Valor']]

def aplicar_transformacion(df, sel_var):
    # Diccionario inicial para casos especiales
    rawdata_to_agg = {
        "Precipitación total diaria": lambda df: df,
        "Precipitación total mensual": lambda df: dvd.PTPM_TT_M(df),
        "Precipitación total anual": lambda df: dvd.PTPM_TT_A(df),
        "Temperatura del aire media diaria": lambda df: dvd.TSSM_MEDIA_D(df),
        "Velocidad del viento media diaria": lambda df: dvd.VVAG_D(df)
    }

    # Intenta primero encontrar la función en el diccionario especial
    funcion = rawdata_to_agg.get(sel_var)

    # Si no se encontró en el diccionario especial, aplicar lógica basada en sufijos
    if funcion is None:
        if "mensual" in sel_var:
            def funcion(df): return dvd.T_VVDAG_MEDIA_M(df)
        elif "anual" in sel_var:
            def funcion(df): return dvd.T_VVDAG_MEDIA_A(df)
        else:
            # Por defecto, si no es mensual o anual, asumir que no necesita transformación
            def funcion(df): return df

    # Aplica la función seleccionada
    stationdf_fnl = funcion(df)

    return stationdf_fnl

def modifdato_LimSup(df, data, selected_variable, codestacion):
    # Volver numérico 'codestacion
    codestacion_n = re.sub("[^0-9]", "", codestacion)
    try:
        codestacion_n = int(codestacion_n)
    except ValueError:
        print("codestacion contiene caracteres no convertibles a int.")
        return df

    # Adaptacion límites según variable    
    if selected_variable == "Precipitación total diaria":
        # Obtener el límite superior para la estación seleccionada
        limite_superior = data.loc[data['CODIGO'] == codestacion_n, 'LimSup']
        if not limite_superior.empty:
            limite_superior = limite_superior.values[0]
        else:
            # Manejo del caso en que no se encuentre un limite_superior
            print(f"No se encontró un límite superior para el código de estación {codestacion}.")
            df['Valor'] = 'ND'
            return df
        
        # Verificar si la columna 'Valor' existe
        if 'Valor' not in df.columns:
            raise KeyError("La columna 'Valor' no existe en el DataFrame.")

        # Evaluar cada fila para determinar si el valor excede el límite superior
        def evaluar_fila(row):
            if row['Valor'] > limite_superior:
                return np.nan  # Asignar NaN para valores que exceden el límite superior
            else:
                return row['Valor']

        # Aplicar la función evaluar_fila
        df['Valor'] = df.apply(evaluar_fila, axis=1)

    return df

# def modifdfprecip_ClasifLimSup(df, data, selected_variable, codestacion):
#     # Definir los bins y las etiquetas para la clasificación
#     bins = [0, 0.1, 10, 20, 40, 60, float('inf')]
#     labels = ['Tiempo seco', 'Lluvia ligera', 'Lluvia ligera a moderada',
#               'Lluvia moderada a fuerte', 'Lluvia fuerte a torrencial', 'Lluvia Torrencial']

#     if selected_variable == "Precipitación total diaria":
#         # Volver numérico 'codestacion
#         codestacion_n = re.sub("[^0-9]", "", codestacion)
#         try:
#             codestacion_n = int(codestacion_n)
#         except ValueError:
#             print("codestacion contiene caracteres no convertibles a int.")
#         # Obtener el límite superior para la estación seleccionada
#         limite_superior = data.loc[data['CODIGO'] == codestacion_n, 'LimSup']#.values[0]
#         if not limite_superior.empty:
#             limite_superior = limite_superior.values[0]
#         else:
#             # Manejo del caso en que no se encuentre un limite_superior
#             print(f"No se encontró un límite superior para el código de estación {codestacion}.")
#             df['Valor'] = 'ND'
#             df['Clasificación'] = 'No aplica'
#             return df
        
#         # Evaluar cada fila para determinar si el valor excede el límite superior
#         def evaluar_fila(row):
#             if row['Valor'] > limite_superior:
#                 return (np.nan, 'No aplica')  # Asignar NaN a 'Valor' y 'No aplica' a 'Clasificación'
#             else:
#                 return (row['Valor'], pd.cut([row['Valor']], bins=bins, labels=labels, right=False)[0])

#         # Aplicar la función evaluar_fila y separar los resultados en dos columnas
#         df[['Valor', 'Clasificación']] = df.apply(evaluar_fila, axis=1, result_type='expand')
#         #df.apply(evaluar_fila, axis=1, result_type='expand')

#     return df

normales = data_normales()
# Función para extraer el valor normal del mes correspondiente
def get_normal_value(row, normales_df, codestacion):
    # Usar el mes para seleccionar la columna correcta
    month_column = row['Mes']
    # Encontrar el valor normal para la estación y el mes específicos
    codestacion_n = re.sub("[^0-9]", "", codestacion)
    try:
        codestacion_n = int(codestacion_n)
    except ValueError:
        print("codestacion contiene caracteres no convertibles a int.")
    normal_value = normales_df.loc[normales_df['Station'] == codestacion_n, month_column]
    return normal_value.values[0] if not normal_value.empty else "Sin dato de ref."

def calculate_indices(stationdf_fnl, normales_df, codestacion):
    # Lógica para calcular índices
    stationdf_fnl['Mes'] = stationdf_fnl['Fecha'].dt.month
    # Aplicar la función para crear una nueva columna con el valor normal
    stationdf_fnl['Valor_Normal'] = stationdf_fnl.apply(lambda row: get_normal_value(row, normales, codestacion), axis=1)
    # Calcular la nueva columna como solicitaste
    stationdf_fnl['Índice (%)'] = ((stationdf_fnl['Valor'] * 100) / stationdf_fnl['Valor_Normal']).round(0)
    stationdf_fnl.drop(columns=['Mes', 'Valor_Normal'], inplace=True)
    return stationdf_fnl

def set_und(selected_variable):
    # Diccionario que mapea prefijos de variables a códigos de sensor
    prefijo_a_und = {
        "Precipitación": 'mm',
        "Temperatura": '°C',
        "Velocidad del viento": 'km/h'
    }

    # Itera sobre los prefijos en el diccionario
    for prefijo, und in prefijo_a_und.items():
        if selected_variable.startswith(prefijo):
            return und

    # Retorna None o un valor por defecto si no se encuentra un prefijo correspondiente
    return None