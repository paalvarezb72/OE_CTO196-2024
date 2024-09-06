import dash
from dash import html
from dash.dependencies import Input, Output, State
import json
import geopy.distance
import plotly.express as px
import dash_leaflet as dl
import base64
import os
import json
import requests
#from docs.replace_data import reemplazar_datos_noEMC, reemplazar_datos_nan, reemplazar_datos_precip, reemplazar_datos
from docs.generate_docs import create_certificate, create_certificate_no_station, select_plantilla, insert_table_in_doc
from utils.helpers import * #(obtener_sensor, construir_rango_fechas, construir_codestacion, 
                           #construir_descripsolicit, fetch_station_data, aplicar_transformacion, 
                           #modifdfprecip_ClasifLimSup, get_normal_value, calculate_indices, 
                           #set_und, calculate_distance)
from utils.db_connection import create_connection
from utils.validation import validate_inputs
from docx import Document
from utils.request_gp.RequestGp import RequestGp
import traceback

import sys
import os
# Añadir la ruta del módulo 'main_firma.py'
ruta_modulo = r'C:/Users/user/Documents/IDEAM/2024/ESRI/herramienta_certificaciones_TyC/geoprocessing-service/app/dummies'
sys.path.append(ruta_modulo)
#from main_firma import main

def register_callbacks(app,data):
    # @app.callback(
    #     Output('distance-info', 'children'),
    #     Input('calculate-distance-btn', 'n_clicks'),
    #     State('map', 'clickData'), #State('mapa-estaciones', 'clickData'),
    #     State('lat-input', 'value'),
    #     State('lon-input', 'value')
    # )
    # def calculate_distance(n_clicks, clickData, lat, lon):
    #     if n_clicks is None or clickData is None:
    #         return html.Div("Seleccione una estación, luego, cuando vea el marcador rojo, introduzca las coordenadas \
    #             de su punto de interés y oprima el botón 'Calcular distancia'.", style={'font-family': 'arial', 'font-size': 13})

    #     estacion_lat = clickData['points'][0]['lat']
    #     estacion_lon = clickData['points'][0]['lon']

    #     if lat is None or lon is None:
    #         return html.Div("Por favor, introduzca las coordenadas del punto de interés.", style={'font-family': 'arial', 'font-size': 13})

    #     distancia = geopy.distance.distance(
    #         (estacion_lat, estacion_lon), (lat, lon)).km
    #     return html.Div(f"La distancia es: {distancia:.2f} km.", style={'font-family': 'arial', 'font-size': 15})

    # Callback para manejar clics en los marcadores
    @app.callback(
        Output("click-info", "children"),
        Input("map", "clickData")
    )
    def display_click_info(click_lat_lng):
        if click_lat_lng is None:
            return "Haga click en el mapa para obtener las coordenadas de su punto de interés"
        print(click_lat_lng) # Ver en consola las coordenadas seleccionadas
        
        coordenadas = (click_lat_lng["latlng"]["lat"], click_lat_lng["latlng"]["lng"])
        return coordenadas
    
    # def obtener_coordenadas(click_lat_lng):
    #     if isinstance(click_lat_lng, str):
    #         try:
    #             click_lat_lng = json.loads(click_lat_lng)  # Convertir de JSON string a dict
    #         except json.JSONDecodeError:
    #             raise ValueError("El valor de clickinfo no es un JSON válido.")

    #     coordenadas = (click_lat_lng["latlng"]["lat"], click_lat_lng["latlng"]["lng"])
    #     return coordenadas

    UPLOAD_DIRECTORY = 'C:/Users/user/Documents/IDEAM/2024/Obligaciones_especificas_ejecucion/OE_8_HerramGeneracionAutomaticaCertif/shp_users_uploaded/'
    @app.callback(
        Output("upload-status", "children"),
        Input("upload-data", "contents"),
        State("upload-data", "filename"),
        #State("upload-data", "last_modified"),
    )
    def upload_zipfile(contents, filename):#, last_modified):
        if contents is not None:
            # Decodifica el contenido del archivo
            content_type, content_string = contents.split(',')
            decoded = base64.b64decode(content_string)
            
            # Guarda el archivo .zip en la ruta especificada
            file_path = os.path.join(UPLOAD_DIRECTORY, filename)
            with open(file_path, "wb") as f:
                f.write(decoded)

            return f'Archivo {filename} cargado y almacenado con éxito.'
        return "No se cargó ningún archivo."
    
    # @app.callback(
    #     [Output('mapa-estaciones', 'figure'),
    #      Output('lat-input', 'value'),
    #      Output('lon-input', 'value')],
    #     [Input('reset-button', 'n_clicks'),
    #      Input('mapa-estaciones', 'clickData')],
    #     prevent_initial_call=True
    # )
    # def update_map(n_clicks, clickData):
    #     ctx = dash.callback_context
    #     triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]

    #     if triggered_id == 'reset-button':
    #         fig = px.scatter_mapbox(data,
    #                                 lat="latitud",
    #                                 lon="longitud",
    #                                 hover_name="nombre",
    #                                 zoom=10,
    #                                 mapbox_style="open-street-map")
    #         return fig, None, None  # Reset everything

    #     if clickData:
    #         lat = clickData['points'][0]['lat']
    #         lon = clickData['points'][0]['lon']
    #         fig = px.scatter_mapbox(data,
    #                                 lat="latitud",
    #                                 lon="longitud",
    #                                 hover_name="nombre",
    #                                 zoom=10,
    #                                 mapbox_style="open-street-map")
    #         fig.add_scattermapbox(lat=[lat], lon=[lon], marker={
    #                               'size': 15, 'color': 'red'})
    #         return fig, None, None  # Update map with the station marker

    #     return dash.no_update

    # @app.callback(
    #     Output('hidden-div', 'children'),
    #     [Input('sin-estaciones', 'value'),
    #      State('lat-input', 'value'),
    #      State('lon-input', 'value')]
    # )
    # def handle_no_station(selection, lat, lon):
    #     if selection == 'no_station':
    #         return json.dumps({'lat': lat, 'lon': lon})
    #     return dash.no_update

    # @app.callback(
    #     [Output('apellidos-input', 'disabled'),
    #     Output('genero-dp', 'disabled'),
    #     Output('genero-input', 'disabled'),
    #     Output('grupetn-dp', 'disabled'),
    #     Output('grupetn-input', 'disabled'),
    #     Output('infpoblac-dp', 'disabled'),
    #     Output('discap-dp', 'disabled'),
    #     Output('discap-input', 'disabled'),
    #     Output('ginteres-dp', 'disabled'),
    #     Output('ginteres-input', 'disabled')],
    #     [Input('tpersona-ri', 'value'),
    #      Input('genero-dp', 'value'),
    #      Input('grupetn-dp', 'value'),
    #      Input('discap-dp','value'),
    #      Input('ginteres-dp','value')]
    # )
    # def update_infopers_dropdowns(tpersona,gender,getn,discap,ginteres):
    #     print(f"tpersona: {tpersona}, gender: {gender}, getn: {getn}, discap: {discap}, ginteres: {ginteres}")
    #     if 'Persona jurídica' in tpersona:
    #             return True,True,True,True,True,True,True,True,False,False
    #     if gender:
    #         if gender != 'Otro':
    #             return False,False,True,False,False,False,False,False,False,False
    #     if getn:
    #         if getn != 'Otro':
    #             return False,False,False,False,True,False,False,False,False,False
    #     if discap:
    #         if discap != 'Otra':
    #             return False,False,False,False,False,False,False,True,False,False
    #     if ginteres:
    #         if ginteres != 'Otro':
    #             return False,False,False,False,False,False,False,False,False,True

    #     return False,False,False,False,False,False,False,False,False,False

    @app.callback(
        [Output('apellidos-input', 'disabled'),
        Output('genero-dp', 'disabled'),
        Output('genero-input', 'disabled'),
        Output('grupetn-dp', 'disabled'),
        Output('grupetn-input', 'disabled'),
        Output('infpoblac-dp', 'disabled'),
        Output('discap-dp', 'disabled'),
        Output('discap-input', 'disabled'),
        Output('ginteres-dp', 'disabled'),
        Output('ginteres-input', 'disabled')],
        [Input('tpersona-ri', 'value'),
        Input('genero-dp', 'value'),
        Input('grupetn-dp', 'value'),
        Input('discap-dp', 'value'),
        Input('ginteres-dp', 'value')]
    )
    def update_infopers_dropdowns(tpersona, gender, getn, discap, ginteres):
        # Evaluar cada input independientemente

        # Si es persona jurídica, deshabilitar todos menos los de grupo de interés
        if tpersona and 'Persona jurídica' in tpersona:
            return [True, True, True, True, True, True, True, True, False, False]

        # Evaluar el dropdown de género
        genero_input_disabled = True if gender != 'Otro' else False
        genero_dp_disabled = False if gender == 'Otro' else False

        # Evaluar el dropdown de grupo étnico
        grupetn_input_disabled = True if getn != 'Otro' else False
        grupetn_dp_disabled = False if getn == 'Otro' else False

        # Evaluar el dropdown de discapacidad
        discap_input_disabled = True if discap != 'Otra' else False
        discap_dp_disabled = False if discap == 'Otra' else False

        # Evaluar el dropdown de grupo de interés
        ginteres_input_disabled = True if ginteres != 'Otro' else False
        ginteres_dp_disabled = False if ginteres == 'Otro' else False

        # Deshabilitar todos los demás campos
        return [
            False,  # apellidos-input siempre habilitado
            genero_dp_disabled,
            genero_input_disabled,
            grupetn_dp_disabled,
            grupetn_input_disabled,
            False,  # infpoblac-dp (no tiene lógica relacionada en tu código)
            discap_dp_disabled,
            discap_input_disabled,
            ginteres_dp_disabled,
            ginteres_input_disabled
        ]
    
    @app.callback(
        [Output('dias-dropdown', 'disabled'),
         Output('meses-dropdown', 'disabled'),
         Output('ano-dropdown', 'disabled')],
        [Input('tiposerie-dp', 'value')]
    )
    def update_date_dropdowns(selected_period):
        if selected_period:
            if 'anual' in selected_period.lower():
                return True, True, False
            elif 'mensual' in selected_period.lower():
                return True, False, False
            elif 'diaria' in selected_period.lower():
                return False, False, False
        return False, False, False

    @app.callback(
        Output("tiposerie-dp", "options"),
        [Input("variable-dp", "value")]
    )
    def set_options(selected_variable):
        if selected_variable == "Precipitación":
            return [{"label": "Precipitación total diaria", "value": "Precipitación total diaria"},
                    {"label": "Precipitación total mensual", "value": "Precipitación total mensual"},
                    {"label": "Precipitación total anual", "value": "Precipitación total anual"}]
        elif selected_variable == "Temperatura máxima":
            return [{"label": "Temperatura máxima diaria", "value": "Temperatura máxima diaria"},
                    {"label": "Temperatura máxima media mensual", "value": "Temperatura máxima media mensual"},
                    {"label": "Temperatura máxima media anual", "value": "Temperatura máxima media anual"}]
        elif selected_variable == "Temperatura mínima":
            return [{"label": "Temperatura mínima diaria", "value": "Temperatura mínima diaria"},
                    {"label": "Temperatura mínima media mensual", "value": "Temperatura mínima media mensual"},
                    {"label": "Temperatura mínima media anual", "value": "Temperatura mínima media anual"}]
        elif selected_variable == "Temperatura del aire":
            return [{"label": "Temperatura del aire media diaria", "value": "Temperatura del aire media diaria"},
                    {"label": "Temperatura del aire media mensual", "value": "Temperatura del aire media mensual"},
                    {"label": "Temperatura del aire media anual", "value": "Temperatura del aire media anual"}]
        elif selected_variable == "Velocidad del viento":
            return [{"label": "Velocidad del viento horaria", "value": "Velocidad del viento horaria"},
                    {"label": "Velocidad del viento media diaria", "value": "Velocidad del viento media diaria"},
                    {"label": "Velocidad del viento media mensual", "value": "Velocidad del viento media mensual"},
                    {"label": "Velocidad del viento media anual", "value": "Velocidad del viento media anual"}]
        return []
    
    plantillas_por_variable = {
        "Precipitación total diaria": "PlantillaPrecipDiaria.docx",
        "Precipitación total mensual": "PlantillaPrecipMensual.docx",
        "Precipitación total anual": "PlantillaPrecipAnual.docx",
        "Temperatura máxima diaria": "PlantillaTemperatDiaria.docx",
        "Temperatura máxima media mensual": "PlantillaTemperatMensual.docx",
        "Temperatura máxima media anual": "PlantillaTemperatAnual.docx",
        "Temperatura mínima diaria": "PlantillaTemperatDiaria.docx",
        "Temperatura mínima media mensual": "PlantillaTemperatMensual.docx",
        "Temperatura mínima media anual": "PlantillaTemperatAnual.docx",
        "Temperatura del aire media diaria": "PlantillaTemperatDiaria.docx",
        "Temperatura del aire media mensual": "PlantillaTemperatMensual.docx",
        "Temperatura del aire media anual": "PlantillaTemperatAnual.docx",
        "Velocidad del viento horaria": "PlantillaVelVientoHoraria.docx",
        "Velocidad del viento media diaria": "PlantillaVelVientoDiaria.docx",
        "Velocidad del viento media mensual": "PlantillaVelVientoMensual.docx",
        "Velocidad del viento media anual": "PlantillaVelVientoAnual.docx",
        "Sin Datos": "PlantillaOficioLamentoSinDatos.docx",
        "Sin Estación": "PlantillaOficioLamentoSinEstaciones.docx"
    }

    # @app.callback(
    #     Output("output-state", "children"),
    #     Input("generar-button", "n_clicks"),
    #     [State("nombres-input", "value"),
    #      State("apellidos-input", "value"),
    #      State("correo-input", "value"),
    #      State("dias-dropdown", "value"),
    #      State("meses-dropdown", "value"),
    #      State("ano-dropdown", "value"),
    #      State("tiposerie-dp", "value"),
    #      State("estacion-dropdown", "value")#,
    #      #State("sin-estaciones", "value"),
    #      #State("lat-input", "value"),
    #      #State("lon-input", "value")
    #      ]
    # )

    # def generar_certificado(n_clicks, nombres, apellidos, correo, dias, meses, ano, selected_variable, estacion_nombre):#, sin_estacion, lat, lon):
    #     if n_clicks is not None:
    #         try:
    #             # Verificar que los campos obligatorios siempre estén llenos
    #             if not (nombres and apellidos and selected_variable ):#and estacion_nombre):
    #                 return html.Div("Por favor, diligencie completamente el formulario para obtener su certificación.",
    #                                 style={'font-family': 'Arial', 'font-style': 'italic', 'color': 'darkred', 'font-size': 13})

    #             # Validar fechas según la periodicidad seleccionada
    #             if (('anual' in selected_variable.lower() and not ano) or
    #                 ('mensual' in selected_variable.lower() and not (meses and ano)) or
    #                 ('diaria' in selected_variable.lower() and not (dias and meses and ano))):
    #                 return html.Div("Por favor, seleccione las fechas correspondientes para obtener su certificación.",
    #                                 style={'font-family': 'Arial', 'font-style': 'italic', 'color': 'darkred', 'font-size': 13})

    #             descrip_solicit = construir_descripsolicit(selected_variable)
    #             # if sin_estacion == 'no_station':
    #             #     if not lat or not lon:
    #             #         return html.Div("Por favor, diligencie los datos de ubicación (lat. y lon.) del punto de interés",
    #             #                         style={'font-family': 'Arial', 'font-style': 'italic', 'color': 'darkred', 'font-size': 13})
    #             #     doc = create_certificate_no_station(nombres, apellidos, correo, descrip_solicit, lat, lon)
    #             #     nombre_archivo_final = f"Modif_{plantillas_por_variable['Sin Estación']}"
    #             #     doc.save(nombre_archivo_final)
    #             #     return html.Div("Respuesta generada para punto de interés sin estaciones cercanas representativas.",
    #             #                     style={'font-family': 'Arial', 'font-style': 'italic', 'color': 'darkorange', 'font-size': 13})
                
    #             estacion_seleccionada = data[data['nombre'] == estacion_nombre].iloc[0]
    #             inicio, fin = construir_rango_fechas(dias, meses, ano)
    #             sensor = obtener_sensor(selected_variable)
    #             codestacion = construir_codestacion(estacion_seleccionada)
                
    #             conn, cur = create_connection()
    #             stationdf = fetch_station_data(cur, inicio, fin, sensor, codestacion)
                
    #             if 'viento' in selected_variable:
    #                 stationdf['Valor'] = (stationdf['Valor'] * 3.6).round(1)

    #             stationdf_fnl = aplicar_transformacion(stationdf, selected_variable)
    #             modifdato_LimSup(stationdf_fnl, data, selected_variable, codestacion)

    #             if selected_variable == "Precipitación total mensual":
    #                 stationdf_fnl = calculate_indices(stationdf_fnl, normales, codestacion)

    #             if selected_variable == "Velocidad del viento horaria":
    #                 stationdf_dv = fetch_station_data(cur, inicio, fin, 'DVAG_CON', codestacion)
    #                 stationdf_dv.rename(columns={'Valor': 'Dirección del viento (°)'}, inplace=True)
    #                 stationdf_fnl = pd.merge(stationdf_dv, stationdf_fnl, on='Fecha')

    #             doc, nombre_plantilla = select_plantilla(selected_variable, stationdf_fnl, nombres, apellidos, correo, dias, meses, ano, estacion_seleccionada, descrip_solicit)
    #             doc = insert_table_in_doc(doc, stationdf_fnl, selected_variable)

    #             nombre_archivo_final = f"Modif_{nombre_plantilla}"
    #             doc.save(nombre_archivo_final)

    #             return html.Div("Se generó la certificación.", style={'font-family': 'Arial', 'font-style': 'italic', 'color': 'darkgreen', 'font-size': 13})
    #         except Exception as e:
    #             error_traceback = traceback.format_exc()
    #             return html.Div([html.Div(f"Intente más tarde, se produjo un error al generar la certificación: {e}",
    #                                       style={'font-family': 'Arial', 'font-style': 'italic', 'color': 'red', 'font-size': 13}),
    #                              html.Pre(error_traceback,
    #                                       style={'font-family': 'Consolas', 'font-style': 'italic', 'color': 'grey', 'font-size': 10})])
    #     return html.Div("Haga clic en este botón para generar la certificación:", style={'font-family': 'Arial', 'font-style': 'italic', 'font-weight': 'bold', 'font-size': 13})

    @app.callback(
        Output("output-represanalis", "children"),#Output("output-state", "children"),
        Input("represanalis-button", "n_clicks"),#Input("generar-button", "n_clicks"),
        [State("file-storage", "data"),  # Obtener el itemid_file guardado
         State("nombres-input", "value"),
         State("apellidos-input", "value"),
         State("correo-input", "value"),
         State("dias-dropdown", "value"),
         State("meses-dropdown", "value"),
         State("ano-dropdown", "value"),
         State("variable-dp", "value"),
         State("tiposerie-dp", "value"),
         State("upload-data", "filename"),
         State("click-info", "children")]
         #State("estacion-dropdown", "value"),
         #State("sin-estaciones", "value"),
         #State("lat-input", "value"),
         #State("lon-input", "value")]
    )

    def generar_certificado(n_clicks, itemid_file, nombres, apellidos, correo, dias, meses, ano, selected_var, selected_variable, upld, clickinfo):#, estacion_nombre, sin_estacion, lat, lon):
        if n_clicks is not None:
            try:
                # Verificar que los campos obligatorios siempre estén llenos
                if not (nombres and apellidos and selected_variable): #and estacion_nombre):
                    return html.Div("Por favor, diligencie completamente el formulario para obtener su certificación.",
                                    style={'font-family': 'Arial', 'font-style': 'italic', 'color': 'darkred', 'font-size': 13})

                # Validar fechas según la periodicidad seleccionada
                if (('anual' in selected_variable.lower() and not ano) or
                    ('mensual' in selected_variable.lower() and not (meses and ano)) or
                    ('diaria' in selected_variable.lower() and not (dias and meses and ano))):
                    return html.Div("Por favor, seleccione las fechas correspondientes para obtener su certificación.",
                                    style={'font-family': 'Arial', 'font-style': 'italic', 'color': 'darkred', 'font-size': 13})

                descrip_solicit = construir_descripsolicit(selected_variable)
                # Llamar las funciones de RequestGP.py
                request_gp = RequestGp()
                data_request = {"variable_meteorologica": selected_var}
                #data_request["variable_meteorologica"] = selected_variable
                if upld:
                    itemid_file = request_gp.upload_file(os.path.join(UPLOAD_DIRECTORY, upld))
                    print(itemid_file)
                    data_request["area_interes_shape"] = itemid_file
                elif clickinfo:
                    #print(f'coord obtenidas {clickinfo}')
                    #coordenadas = display_click_info(clickinfo)
                    data_request["area_interes_coordenadas"] = clickinfo
                print(data_request)
                resultado_gp = request_gp.ejecutar_geoprocesamiento(data_request)
                print(resultado_gp)
                if resultado_gp["status"] == "NO_STATION":                
                    doc = create_certificate_no_station(nombres, apellidos, correo, descrip_solicit, clickinfo)
                    nombre_archivo_final = f"Modif_{plantillas_por_variable['Sin Estación']}"
                    doc.save(nombre_archivo_final)
                    return html.Div("Respuesta generada para punto de interés sin estaciones cercanas representativas.",
                                    style={'font-family': 'Arial', 'font-style': 'italic', 'color': 'darkorange', 'font-size': 13})
                
                elif resultado_gp["status"] == "OK":
                    cod_estacion = resultado_gp["message"]
                    estacion_seleccionada = data[data['CODIGO'] == cod_estacion].iloc[0]
                    inicio, fin = construir_rango_fechas(dias, meses, ano)
                    sensor = obtener_sensor(selected_variable)
                    codestacion = construir_codestacion(estacion_seleccionada)

                    conn, cur = create_connection()
                    stationdf = fetch_station_data(cur, inicio, fin, sensor, codestacion)
                    
                    if 'viento' in selected_variable:
                        stationdf['Valor'] = (stationdf['Valor'] * 3.6).round(1)

                    stationdf_fnl = aplicar_transformacion(stationdf, selected_variable)
                    modifdato_LimSup(stationdf_fnl, data, selected_variable, codestacion)

                    if selected_variable == "Precipitación total mensual":
                        stationdf_fnl = calculate_indices(stationdf_fnl, normales, codestacion)

                    if selected_variable == "Velocidad del viento horaria":
                        stationdf_dv = fetch_station_data(cur, inicio, fin, 'DVAG_CON', codestacion)
                        stationdf_dv.rename(columns={'Valor': 'Dirección del viento (°)'}, inplace=True)
                        stationdf_fnl = pd.merge(stationdf_fnl, stationdf_dv, on='Fecha')

                    doc, nombre_plantilla = select_plantilla(selected_variable, stationdf_fnl, nombres, apellidos, correo, dias, meses, ano, estacion_seleccionada, descrip_solicit)
                    doc = insert_table_in_doc(doc, stationdf_fnl, selected_variable)

                    nombre_archivo_final = f"Modif_{nombre_plantilla}"
                    doc.save(nombre_archivo_final)
                    return html.Div("Se generó la certificación.", style={'font-family': 'Arial', 'font-style': 'italic', 'color': 'darkgreen', 'font-size': 13})
                
                elif resultado_gp["status"] == "ERROR":
                    return html.Div(resultado_gp["message"],
                                    style={'font-family': 'Arial', 'font-style': 'italic', 'color': 'darkred', 'font-size': 13})
                else:
                    mensaje_faltante = resultado_gp["message"]
                    return html.Div(f"No se pudo procesar la solicitud,{mensaje_faltante}", style={'font-family': 'Arial', 'font-style': 'italic', 'color': 'darkred', 'font-size': 13})
                
            except Exception as e:
                error_traceback = traceback.format_exc()
                return html.Div([html.Div(f"Intente más tarde, se produjo un error al generar la certificación: {e}",
                                          style={'font-family': 'Arial', 'font-style': 'italic', 'color': 'red', 'font-size': 13}),
                                 html.Pre(error_traceback,
                                          style={'font-family': 'Consolas', 'font-style': 'italic', 'color': 'grey', 'font-size': 10})])
        return html.Div("Haga clic en este botón para generar la certificación:", style={'font-family': 'Arial', 'font-style': 'italic', 'font-weight': 'bold', 'font-size': 13})
