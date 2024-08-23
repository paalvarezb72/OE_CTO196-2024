# Extracción tabla Cassandra y cálculo de derivadas para certificaciones
import pandas as pd
import numpy as np

# Precipitación total mensual
def PTPM_TT_M(df, columna_fecha='Fecha', columna_valor='Valor', porc_min=0.7):    
    if not pd.api.types.is_datetime64_any_dtype(df[columna_fecha]):
        df[columna_fecha] = pd.to_datetime(df[columna_fecha])
    
    df.set_index(columna_fecha, inplace=True)
    
    # Resample y sumar valores
    ptpm_tt_m = df[columna_valor].resample('M').sum()
    
    # Calcular el número de días esperados en cada mes
    days_in_month = ptpm_tt_m.index.to_series().dt.days_in_month
    
    # Recuento de datos por mes
    counts = df[columna_valor].resample('M').count()
    
    # Filtrado: donde el recuento es menor al porcentaje mínimo esperado, reemplazar por NaN
    ptpm_tt_m = ptpm_tt_m.where(counts >= days_in_month * porc_min, other=float('nan'))
    
    ptpm_tt_m = ptpm_tt_m.reset_index()
    
    return ptpm_tt_m

def PTPM_TT_A(df, columna_fecha='Fecha', columna_valor='Valor', porc_min=0.75):    
    if not pd.api.types.is_datetime64_any_dtype(df[columna_fecha]):
        df[columna_fecha] = pd.to_datetime(df[columna_fecha])
    
    df.set_index(columna_fecha, inplace=True)

    # Obtener la suma mensual como antes
    ptpm_tt_m = PTPM_TT_M(df, columna_fecha, columna_valor, porc_min)

    # Calcular la cantidad de meses válidos por año
    counts = ptpm_tt_m[columna_valor].notna().resample('Y').sum()
    
    # Resample anual para sumar la precipitación mensual
    ptpm_tt_a = ptpm_tt_m[columna_valor].resample('Y').sum()
    
    # Filtrar: si no hay suficientes meses válidos, reemplazar por NaN
    ptpm_tt_a = ptpm_tt_a.where(counts >= 12 * porc_min, other=float('nan'))

    ptpm_tt_a = ptpm_tt_a.reset_index()
    
    return ptpm_tt_a

# Precipitación total mensual
# def PTPM_TT_M(df, columna_fecha='Fecha', columna_valor='Valor', porc_min=0.7):    
#     # Convertir la columna de fecha a datetime si aún no lo es
#     if not pd.api.types.is_datetime64_any_dtype(df[columna_fecha]):
#         df[columna_fecha] = pd.to_datetime(df[columna_fecha])
    
#     # Establecer la columna 'Fecha' como índice
#     df.set_index(columna_fecha, inplace=True)
    
#     days_in_month = df.index.to_series().dt.days_in_month
#     days_in_month = days_in_month.resample('M').first()
    
#     # Función para verificar si un día específica tiene suficientes datos
#     def complet_mes(sub_df):
#         mes = sub_df.index[0].month
#         total_esperado = days_in_month[days_in_month.index.month == mes].iloc[0]
#         return len(sub_df) >= total_esperado * porc_min

#     # Luego de establecer el índice, aplicar resample
#     df_filtrado = df.groupby([df.index.year, df.index.month]).filter(complet_mes)
#     if df_filtrado.empty:
#         print(f"DataFrame vacío después de filtrar por meses válidos.")
#         return df_filtrado
#     # Se hacen operaciones de suma                
#     ptpm_tt_m = df_filtrado[['Valor']].resample('M').sum()
    
#     # Reemplazar sumas de 0 con NaN si no cumplen con el porcentaje mínimo
#     counts = df.groupby([df.index.year, df.index.month])[columna_valor].count()
#     counts.index = pd.to_datetime(['{}-{}'.format(i[0], i[1]) for i in counts.index], format='%Y-%m')
#     counts = counts.resample('M').sum().round(1)
#     ptpm_tt_m['Valor'] = ptpm_tt_m['Valor'].where(counts >= days_in_month * porc_min, other=float('nan'))
    
#     # Reset index
#     ptpm_tt_m.reset_index(inplace=True)
    
#     return ptpm_tt_m

# # Precipitación total anual
# def PTPM_TT_A(df, columna_fecha='Fecha', columna_valor='Valor', porc_min=0.75):    
#     if df.empty:
#         return df
#     # Convertir la columna de fecha a datetime si aún no lo es
#     if not pd.api.types.is_datetime64_any_dtype(df[columna_fecha]):
#         df[columna_fecha] = pd.to_datetime(df[columna_fecha])
    
#     # Función para verificar si una hora específica tiene suficientes datos
#     def complet_anio(sub_df):
#         return len(sub_df) >= 12 * porc_min
       
#     # Antes de resample, establecer la columna 'Fecha' como índice
#     df.set_index(columna_fecha, inplace=True)

#     # Luego de establecer el índice, aplicar resample
#     df_filtrado = df.groupby([df.index.year]).filter(complet_anio)
#     # Si el df_filtrado está vacío, se devuelve
#     if df_filtrado.empty:
#         print(f"DataFrame vacío después de filtrar por años válidos.")
#         return df_filtrado
#     # Se hacen operaciones de suma
#     ptpm_tt_a = df_filtrado[['Valor']].resample('Y').sum()
    
#     # Reemplazar sumas de 0 con NaN si no cumplen con el porcentaje mínimo
#     counts = df_filtrado.groupby(df_filtrado.index.year)[columna_valor].count()
#     counts.index = pd.to_datetime(['{}-01'.format(i) for i in counts.index], format='%Y-%m')
#     counts = counts.resample('Y').sum().round(1)
#     ptpm_tt_a['Valor'] = ptpm_tt_a['Valor'].where(counts >= 12 * porc_min, other=float('nan'))

#     # Reset index
#     ptpm_tt_a.reset_index(inplace=True)
    
#     return ptpm_tt_a

# Vel viento media diaria
def VVAG_D(df, columna_fecha='Fecha', columna_valor='Valor', porc_min=0.7):
    # Convertir la columna de fecha a datetime si aún no lo es
    if not pd.api.types.is_datetime64_any_dtype(df[columna_fecha]):
        df[columna_fecha] = pd.to_datetime(df[columna_fecha])

    # Establecer la columna 'Fecha' como índice
    df.set_index(columna_fecha, inplace=True)
    
    # Calcular el total de registros esperados por día (24 horas)
    total_esperado_por_dia = 24
    
    # Resample y calcular la media diaria
    vvag_med_d = df[columna_valor].resample('D').mean().round(1)
    
    # Recuento de datos por día
    counts = df[columna_valor].resample('D').count()
    
    # Filtrar: donde el recuento es menor al porcentaje mínimo esperado, reemplazar por NaN
    vvag_med_d = vvag_med_d.where(counts >= total_esperado_por_dia * porc_min, other=float('nan'))
    
    vvag_med_d = vvag_med_d.reset_index()
    
    return vvag_med_d
# def VVAG_D(df, columna_fecha='Fecha', columna_valor='Valor', porc_min=0.7):
#     # Convertir la columna de fecha a datetime si aún no lo es
#     if not pd.api.types.is_datetime64_any_dtype(df[columna_fecha]):
#         df[columna_fecha] = pd.to_datetime(df[columna_fecha])

#     # Función para verificar si un día pluviométrico tiene suficientes datos
#     def complet_dia(sub_df):
#         return len(sub_df) >= total_esperado_por_dia * porc_min

#     # Calcular el total de registros esperados por día pluviométrico
#     total_esperado_por_dia = 24
    
#     # Establecer la columna 'Fecha' como índice
#     df.set_index(columna_fecha, inplace=True)
#     # Filtrar días que tienen suficientes datos
#     df_completo = df.groupby([df.index.year, df.index.month, df.index.day]).filter(complet_dia)
#     vvag_med_d = df_completo[['Valor']].resample('D').mean().round(1)
#     vvag_med_d.reset_index(inplace=True)
    
#     return vvag_med_d

def procesar_dia(df):
    horas = df.index.hour.unique()
    if df[df['Valor'].notna()]['Valor'].count() < 3:
        return np.nan
    elif set(horas) == set([7, 13, 18]):
        return df[df['Valor'].notna()]['Valor'].astype(float).mean().round(1)
    elif set(horas) == set([7, 13, 19]):
        v7, v13, v19 = df.loc[df.index.hour.isin([7, 13, 19]) & df['Valor'].notna(), 'Valor'].astype(float)
        return ((v7 + v13 + 2*v19) / 4).round(1)
    else:
        return np.nan
    
def TSSM_MEDIA_D(df, columna_fecha='Fecha', columna_valor='Valor'):
    # Convertir la columna de fecha a datetime si aún no lo es
    if not pd.api.types.is_datetime64_any_dtype(df[columna_fecha]):
        df[columna_fecha] = pd.to_datetime(df[columna_fecha])
        
    df.set_index('Fecha', inplace=True)
    
    tssm_media_d = df.resample('D').apply(procesar_dia).reset_index()
        
    tssm_media_d.columns = ['Fecha', 'Valor']
    
    return tssm_media_d

def T_VVDAG_MEDIA_M(df, columna_fecha='Fecha', columna_valor='Valor', porc_min=0.67):
    # Convertir la columna de fecha a datetime si aún no lo es
    if not pd.api.types.is_datetime64_any_dtype(df[columna_fecha]):
        df[columna_fecha] = pd.to_datetime(df[columna_fecha])
    
    # Establecer la columna 'Fecha' como índice
    df.set_index(columna_fecha, inplace=True)
    
    # Calcular el número de días por mes
    days_in_month = df.index.to_series().dt.days_in_month.resample('M').first()

    # Resample y calcular la media mensual
    t2m_med_m = df[columna_valor].resample('M').mean().round(1)
    
    # Recuento de datos por mes
    counts = df[columna_valor].resample('M').count()
    # Alinear los índices de `counts` y `days_in_month`
    counts, days_in_month = counts.align(days_in_month, join='left')

    # Filtrar: donde el recuento es menor al porcentaje mínimo esperado, reemplazar por NaN
    t2m_med_m = t2m_med_m.where(counts >= days_in_month * porc_min, other=float('nan'))
    
    t2m_med_m = t2m_med_m.reset_index()
    t2m_med_m.columns = ['Fecha', 'Valor']
    
    return t2m_med_m

def T_VVDAG_MEDIA_A(df, columna_fecha='Fecha', columna_valor='Valor', porc_min=0.67):
    # Convertir la columna de fecha a datetime si aún no lo es
    if not pd.api.types.is_datetime64_any_dtype(df[columna_fecha]):
        df[columna_fecha] = pd.to_datetime(df[columna_fecha])
    
    # Obtener la media mensual utilizando la función T_VVDAG_MEDIA_M
    t2m_med_m = T_VVDAG_MEDIA_M(df, columna_fecha, columna_valor, porc_min)
    
    # Asegurarse de que el índice sea un DatetimeIndex
    t2m_med_m.set_index('Fecha', inplace=True)
    
    # Calcular la cantidad de meses válidos por año
    counts = t2m_med_m['Valor'].notna().resample('Y').sum()
    
    # Resample anual para calcular la media anual
    t2m_med_a = t2m_med_m['Valor'].resample('Y').mean().round(1)
    
    # Filtrar: si no hay suficientes meses válidos, reemplazar por NaN
    t2m_med_a = t2m_med_a.where(counts >= 12 * porc_min, other=float('nan'))

    t2m_med_a = t2m_med_a.reset_index()
    
    return t2m_med_a

# # Temperatura (máxima, mínima y del aire) media mensual
# def T_VVDAG_MEDIA_M(df, columna_fecha='Fecha', columna_valor='Valor', porc_min=0.67):    
#     df.reset_index(inplace=True)
#     # Convertir la columna de fecha a datetime si aún no lo es
#     if not pd.api.types.is_datetime64_any_dtype(df[columna_fecha]):
#         df[columna_fecha] = pd.to_datetime(df[columna_fecha])
    
#     # Establecer la columna 'Fecha' como índice
#     df.set_index(columna_fecha, inplace=True)
    
#     days_in_month = df.index.to_series().dt.days_in_month
#     days_in_month = days_in_month.resample('M').first()
    
#     # Función para verificar si una hora específica tiene suficientes datos
#     def complet_mes(sub_df):
#         mes = sub_df.index[0].month
#         total_esperado = days_in_month[days_in_month.index.month == mes].iloc[0]
#         return len(sub_df) >= total_esperado * porc_min

#     # Luego de establecer el índice, aplicar resample
#     df_filtrado = df.groupby([df.index.year, df.index.month]).filter(complet_mes)
#     t2m_med_m = df_filtrado[['Valor']].resample('M').mean().round(1)
#     t2m_med_m.reset_index(inplace=True)
#     t2m_med_m.columns = ['Fecha', 'Valor']
    
#     return t2m_med_m

# # Temperatura (máxima, mínima y del aire) media anual
# def T_VVDAG_MEDIA_A(df, columna_fecha='Fecha', columna_valor='Valor', porc_min=0.67):
#     df.reset_index(inplace=True)
#     # Convertir la columna de fecha a datetime si aún no lo es
#     if not pd.api.types.is_datetime64_any_dtype(df[columna_fecha]):
#         df[columna_fecha] = pd.to_datetime(df[columna_fecha])
    
#     # Función para verificar si una hora específica tiene suficientes datos
#     def complet_anio(sub_df):
#         return len(sub_df) >= 12 * porc_min
       
#     # Antes de resample, establecer la columna 'Fecha' como índice
#     df.set_index(columna_fecha, inplace=True)

#     # Luego de establecer el índice, aplicar resample
#     df_filtrado = df.groupby([df.index.year]).filter(complet_anio)
#     t2m_med_a = df_filtrado[['Valor']].resample('Y').mean().round(1)
#     t2m_med_a.reset_index(inplace=True)
    
#     return t2m_med_a



