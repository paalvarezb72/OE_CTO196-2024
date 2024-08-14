# Extracción tabla Cassandra y cálculo de derivadas para certificaciones
import pandas as pd
import numpy as np

# Precipitación total mensual
def PTPM_TT_M(df, columna_fecha='Fecha', columna_valor='Valor', porc_min=0.7):    
    # Convertir la columna de fecha a datetime si aún no lo es
    if not pd.api.types.is_datetime64_any_dtype(df[columna_fecha]):
        df[columna_fecha] = pd.to_datetime(df[columna_fecha])
    
    # Establecer la columna 'Fecha' como índice
    df.set_index(columna_fecha, inplace=True)
    
    days_in_month = df.index.to_series().dt.days_in_month
    days_in_month = days_in_month.resample('M').first()
    
    # Función para verificar si una hora específica tiene suficientes datos
    def complet_mes(sub_df):
        mes = sub_df.index[0].month
        total_esperado = days_in_month[days_in_month.index.month == mes].iloc[0]
        return len(sub_df) >= total_esperado * porc_min

    # Luego de establecer el índice, aplicar resample
    df_filtrado = df.groupby([df.index.year, df.index.month]).filter(complet_mes)
    # Se hacen operaciones de suma                
    ptpm_tt_m = df_filtrado[['Valor']].resample('M').sum()
    
    # Reemplazar sumas de 0 con NaN si no cumplen con el porcentaje mínimo
    counts = df.groupby([df.index.year, df.index.month])[columna_valor].count()
    counts.index = pd.to_datetime(['{}-{}'.format(i[0], i[1]) for i in counts.index], format='%Y-%m')
    counts = counts.resample('M').sum().round(1)
    ptpm_tt_m['Valor'] = ptpm_tt_m['Valor'].where(counts >= days_in_month * porc_min, other=float('nan'))
    
    # Reset index
    ptpm_tt_m.reset_index(inplace=True)
    
    return ptpm_tt_m

# Precipitación total anual
def PTPM_TT_A(df, columna_fecha='Fecha', columna_valor='Valor', porc_min=0.75):    
    # Convertir la columna de fecha a datetime si aún no lo es
    if not pd.api.types.is_datetime64_any_dtype(df[columna_fecha]):
        df[columna_fecha] = pd.to_datetime(df[columna_fecha])
    
    # Función para verificar si una hora específica tiene suficientes datos
    def complet_anio(sub_df):
        return len(sub_df) >= 12 * porc_min
       
    # Antes de resample, establecer la columna 'Fecha' como índice
    df.set_index(columna_fecha, inplace=True)

    # Luego de establecer el índice, aplicar resample
    df_filtrado = df.groupby([df.index.year]).filter(complet_anio)
    # Se hacen operaciones de suma
    ptpm_tt_a = df_filtrado[['Valor']].resample('Y').sum()
    
    # Reemplazar sumas de 0 con NaN si no cumplen con el porcentaje mínimo
    counts = df.groupby(df.index.year)[columna_valor].count()
    counts.index = pd.to_datetime(['{}-01'.format(i) for i in counts.index], format='%Y-%m')
    counts = counts.resample('Y').sum().round(1)
    ptpm_tt_a['Valor'] = ptpm_tt_a['Valor'].where(counts >= 12 * porc_min, other=float('nan'))

    # Reset index
    ptpm_tt_a.reset_index(inplace=True)
    
    return ptpm_tt_a

# Vel viento media diaria
def VVAG_D(df, columna_fecha='Fecha', columna_valor='Valor', porc_min=0.7):
    # Convertir la columna de fecha a datetime si aún no lo es
    if not pd.api.types.is_datetime64_any_dtype(df[columna_fecha]):
        df[columna_fecha] = pd.to_datetime(df[columna_fecha])

    # Función para verificar si un día pluviométrico tiene suficientes datos
    def complet_dia(sub_df):
        return len(sub_df) >= total_esperado_por_dia * porc_min

    # Calcular el total de registros esperados por día pluviométrico
    total_esperado_por_dia = 24
    
    # Establecer la columna 'Fecha' como índice
    df.set_index(columna_fecha, inplace=True)
    # Filtrar días que tienen suficientes datos
    df_completo = df.groupby([df.index.year, df.index.month, df.index.day]).filter(complet_dia)
    vvag_med_d = df_completo[['Valor']].resample('D').mean().round(1)
    vvag_med_d.reset_index(inplace=True)
    
    return vvag_med_d

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

# Temperatura (máxima, mínima y del aire) media mensual
def T_VVDAG_MEDIA_M(df, columna_fecha='Fecha', columna_valor='Valor', porc_min=0.67):    
    df.reset_index(inplace=True)
    # Convertir la columna de fecha a datetime si aún no lo es
    if not pd.api.types.is_datetime64_any_dtype(df[columna_fecha]):
        df[columna_fecha] = pd.to_datetime(df[columna_fecha])
    
    # Establecer la columna 'Fecha' como índice
    df.set_index(columna_fecha, inplace=True)
    
    days_in_month = df.index.to_series().dt.days_in_month
    days_in_month = days_in_month.resample('M').first()
    
    # Función para verificar si una hora específica tiene suficientes datos
    def complet_mes(sub_df):
        mes = sub_df.index[0].month
        total_esperado = days_in_month[days_in_month.index.month == mes].iloc[0]
        return len(sub_df) >= total_esperado * porc_min

    # Luego de establecer el índice, aplicar resample
    df_filtrado = df.groupby([df.index.year, df.index.month]).filter(complet_mes)
    t2m_med_m = df_filtrado[['Valor']].resample('M').mean().round(1)
    t2m_med_m.reset_index(inplace=True)
    t2m_med_m.columns = ['Fecha', 'Valor']
    
    return t2m_med_m

# Temperatura (máxima, mínima y del aire) media anual
def T_VVDAG_MEDIA_A(df, columna_fecha='Fecha', columna_valor='Valor', porc_min=0.67):
    df.reset_index(inplace=True)
    # Convertir la columna de fecha a datetime si aún no lo es
    if not pd.api.types.is_datetime64_any_dtype(df[columna_fecha]):
        df[columna_fecha] = pd.to_datetime(df[columna_fecha])
    
    # Función para verificar si una hora específica tiene suficientes datos
    def complet_anio(sub_df):
        return len(sub_df) >= 12 * porc_min
       
    # Antes de resample, establecer la columna 'Fecha' como índice
    df.set_index(columna_fecha, inplace=True)

    # Luego de establecer el índice, aplicar resample
    df_filtrado = df.groupby([df.index.year]).filter(complet_anio)
    t2m_med_a = df_filtrado[['Valor']].resample('Y').mean().round(1)
    t2m_med_a.reset_index(inplace=True)
    
    return t2m_med_a



