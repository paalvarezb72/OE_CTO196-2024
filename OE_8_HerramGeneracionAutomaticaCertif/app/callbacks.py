# app/callbacks.py
import dash
import base64
import os
import traceback
import sys
import dash_leaflet as dl
from dash import html, dcc
from datetime import date, datetime
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from docs.generate_docs import *
from docs.convert_a_pdf import convertir_a_pdf
from utils.helpers import *
from utils.db_connection import create_connection
from utils.request_gp.RequestGp import RequestGp
from utils.request_gp.update_table import UpdateTable

# Añadir la ruta del módulo 'main_firma.py'
ruta_modulo = r'C:/Users/user/Documents/IDEAM/2024/ESRI/herramienta_certificaciones_TyC/geoprocessing-service/app/dummies'
sys.path.append(ruta_modulo)
#from main_firma import main

def register_callbacks(app,data):
    # Callback para manejar clics en los marcadores
    @app.callback(
        Output("click-info", "children"),
        Input("map", "clickData")
    )
    def display_click_info(click_lat_lng):
        if click_lat_lng is None:
            msg_click = html.Div("Si no cargó ningún shape, haga click en el mapa para obtener las coordenadas de \
                                  su punto de interés aquí.",
                             style={'font-family': 'Arial', 'font-style': 'italic', 'font-weight':'bold', 'font-size': 16})
            return msg_click
        print(f"Las coordenadas seleccinadas fueron: {click_lat_lng}") # Ver en consola las coordenadas seleccionadas
        
        coordenadas = (click_lat_lng["latlng"]["lat"], click_lat_lng["latlng"]["lng"])
        return coordenadas

    base_dir = os.path.dirname(os.path.abspath(__file__))  # Obtiene el directorio de callbacks.py
    UPLOAD_DIRECTORY = os.path.join(base_dir, "../user_shp_uploaded/")

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
        msgupload = html.Div("No se ha cargado ningún archivo.",
                             style={'font-family': 'Arial', 'font-style': 'italic', 'font-size': 16})
        return msgupload

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
            return [True, True, True, True, True, True, True, True, False, True]

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
            False,  # infpoblac-dp siempre habilitado
            discap_dp_disabled,
            discap_input_disabled,
            ginteres_dp_disabled,
            ginteres_input_disabled
        ]

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

    # Callback que sincroniza los rangos permitidos entre fecha inicial y fecha final
    @app.callback(
        Output('inidate-pckr', 'maxDate'),
        Output('findate-pckr', 'minDate'),
        Input('inidate-pckr', 'value'),
        Input('findate-pckr', 'value')
    )
    def actualizar_rango_fechas(fecha_inicio, fecha_fin):
        """
        Sincroniza los rangos permitidos entre fecha inicial y fecha final.
        """
        # Verificar y procesar fechas
        if fecha_inicio:
            fecha_inicio = datetime.strptime(fecha_inicio.split('T')[0], '%Y-%m-%d').date()
            #fecha_inicio = parse_fecha(fecha_inicio)
        else:
            fecha_inicio = date(1955, 1, 1)
        
        if fecha_fin:
            #fecha_fin = parse_fecha(fecha_fin)
            fecha_fin = datetime.strptime(fecha_fin.split('T')[0], '%Y-%m-%d').date()
        else:
            fecha_fin = datetime.now().date()

        # Actualizar restricciones
        max_fecha_inicio = fecha_fin  # La fecha inicial no puede ser después de la fecha final
        min_fecha_fin = fecha_inicio  # La fecha final no puede ser antes de la fecha inicial

        return max_fecha_inicio, min_fecha_fin

    # # Callback para actualizar el calendario según el año del slider
    # @app.callback(
    #     Output('inidate-pckr', 'value'),
    #     Input('inyear-slider', 'value'),
    #     State('inidate-pckr', 'value')
    # )
    # def update_date(year, current_date):
    #     """
    #     Actualiza la fecha visible del DatePickerSingle al año seleccionado en el slider de inidate,
    #     manteniendo el mismo mes y día.
    #     """
    #     # Convertir la fecha actual en un objeto datetime
    #     current_date_obj = parse_fecha(current_date).date()
        
    #     # Crear una nueva fecha con el año del slider
    #     new_date = current_date_obj.replace(year=year)
        
    #     # Retornar la nueva fecha como cadena en formato ISO
    #     return new_date.strftime('%Y-%m-%d')# %H:%M:%S.%f')
    

    # # Callback para actualizar el calendario final según el año del slider
    # @app.callback(
    #     Output('findate-pckr', 'value'),
    #     Input('finyear-slider', 'value'),
    #     State('findate-pckr', 'value')
    # )
    # def update_date(year, current_date):
    #     """
    #     Actualiza la fecha visible del DatePickerSingle al año seleccionado en el slider de findate,
    #     manteniendo el mismo mes y día.
    #     """
    #     # Convertir la fecha actual en un objeto datetime
    #     current_date_obj = parse_fecha(current_date).date()
        
    #     # Crear una nueva fecha con el año del slider
    #     new_date = current_date_obj.replace(year=year)
        
    #     # Retornar la nueva fecha como cadena en formato ISO
    #     return new_date.strftime('%Y-%m-%d')# %H:%M:%S.%f')

    # Este callback toma la estación seleccionada del dropdown y actualiza el mapa

    @app.callback(
        [Output("map", "center"),  
        Output("map", "zoom"),    
        Output("click-layer", "children")],  
        [Input("estacion-dropdown", "value")],  # Input del dropdown
        [State("map", "center"), State("map", "zoom")]  # Estado actual del mapa
    )
    def actualizar_mapa(nombre_estacion, current_center, current_zoom):
        print(f"Callback ejecutado. Estación seleccionada: {nombre_estacion}")

        if not nombre_estacion:
            print("No se ha seleccionado ninguna estación.")
            raise PreventUpdate

        estaciones_filtradas = data[data['nombre'] == nombre_estacion]
        print(f"Número de estaciones encontradas: {len(estaciones_filtradas)}")

        if estaciones_filtradas.empty:
            print("No se encontraron estaciones con ese nombre.")
            raise PreventUpdate  

        estacion_seleccionada = estaciones_filtradas.iloc[0]
        nueva_lat = float(estacion_seleccionada["latitud"])
        nueva_lon = float(estacion_seleccionada["longitud"])

        #print(f"Coordenadas de la estación seleccionada: lat={nueva_lat}, lon={nueva_lon}") #for checking

        # Restablecer el zoom solo si está fuera de un rango aceptable
        zoom_minimo = 2
        zoom_maximo = 25
        nuevo_zoom = current_zoom if zoom_minimo <= current_zoom <= zoom_maximo else 12
        
        marcador = dl.Marker(
            position=[nueva_lat, nueva_lon],
            children=[dl.Tooltip(f"Nombre: {estacion_seleccionada['nombre']}, Altitud: {estacion_seleccionada['altitudDEM']} m")]
        )

        return [[nueva_lat, nueva_lon], nuevo_zoom, [marcador]]  # Se actualiza centro, zoom y marcador
# Zoom corregido  # Centro, zoom y marcador
    

    # @app.callback(
    #     Output("mapa-estacion", "figure"),
    #     [Input("estacion-dropdown", "value")]
    # )
    # def actualizar_mapa(nombre_estacion):
    #     print(f"Nombre de estación recibido del dropdown: {nombre_estacion}")
    #     estaciones_filtradas = data[data['nombre'] == nombre_estacion]
    #     print(f"Numero de estaciones encontradas: {len(estaciones_filtradas)}")

    #     if not estaciones_filtradas.empty:
    #         estacion_seleccionada = estaciones_filtradas.iloc[0]
    #         fig.update_layout(mapbox_center={"lat": estacion_seleccionada["latitud"], "lon": estacion_seleccionada["longitud"]})
    #         return fig
    #     else:
    #         print("No se encontraron estaciones con ese nombre.")
    #         raise PreventUpdate


    @app.callback(
        [Output("gp-result-store", "data"), #Output("output-represanalis", "children"),
         Output("output-state", "children"),
         Output("certtyc-result-store", "data"),
         Output("pdf_data", "data"),
         Output("message-store", "data")],
        Input("represanalis-button", "n_clicks"),#Input("generar-button", "n_clicks"),
        [State("file-storage", "data"),  # Obtener el itemid_file guardado
         State("tpersona-ri","value"),
         State("tdoc-dp", "value"),
         State("ndoc-input", "value"),
         State("nombres-input", "value"),
         State("apellidos-input", "value"),
         State("genero-dp", "value"),
         State("grupetn-dp", "value"),
         State("infpoblac-dp", "value"),
         State("discap-dp", "value"),
         State("ginteres-dp", "value"),
         State("correo-input", "value"),
         State("tel-input", "value"),
         State("inidate-pckr", "value"),
         State("findate-pckr", "value"),
         State("variable-dp", "value"),
         State("tiposerie-dp", "value"),
         State("upload-data", "filename"),
         State("click-info", "children")]
    )

    def generar_certificado(n_clicks, itemid_file, tpers, tdoc, ndoc, nombres, apellidos, gendp, getndp, infpob, discdp, gintdp,
                            correo, tel, fecha_inicio, fecha_fin, selected_var, selected_variable, upld, clickinfo):#, estacion_nombre, sin_estacion, lat, lon):
        if n_clicks is not None:
            try:
                # Verificar que los campos obligatorios siempre estén llenos
                if tpers == 'Persona jurídica':
                    if not (tdoc and ndoc and nombres and gintdp and correo and tel and selected_variable and fecha_inicio): #and estacion_nombre):
                        message_sdpj = "Por favor, diligencie completamente el formulario para obtener su certificación."
                        return (None, html.Div(message_sdpj,
                                            style={'font-family': 'Arial', 'font-style': 'italic', 'color': 'darkred', 'font-size': 16}),
                                None, None, message_sdpj)
                elif tpers == 'Persona natural':
                    if not (tdoc and ndoc and nombres and apellidos and gendp and getndp and infpob and discdp and
                            gintdp and correo and tel and fecha_inicio and selected_variable): #and estacion_nombre):
                        message_sdpn = "Por favor, diligencie completamente el formulario para obtener su certificación."
                        return (None, html.Div(message_sdpn,
                                            style={'font-family': 'Arial', 'font-style': 'italic', 'color': 'darkred', 'font-size': 16}),
                                None, None, message_sdpn)

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
                    print(f'coord obtenidas {clickinfo}')
                    coord_tupla = (clickinfo[1], clickinfo[0])
                    coord_tupla_tipo = type(coord_tupla)
                    print(f'Tipo dato coords: {coord_tupla_tipo}')
                    data_request["area_interes_coordenadas"] = coord_tupla
                print(data_request)
                resultado_gp = request_gp.ejecutar_geoprocesamiento(data_request)
                print(resultado_gp)
                if resultado_gp["status"] == "NO_STATION":            
                    doc = create_certificate_no_station(tpers, nombres, apellidos, correo, descrip_solicit, clickinfo)
                    date_rnow_str = datetime.now().strftime("%Y%m%d_%H%M%S")
                    nombre_archivo_final = f"{date_rnow_str}_{plantillas_por_variable['Sin Estación']}"
                    doc.save(nombre_archivo_final)
                    pdf_path = convertir_a_pdf(nombre_archivo_final)
                    print(f'El path es {pdf_path}')
                    if pdf_path is None:
                        message_sp = "No se pudo generar el archivo PDF"
                        return (resultado_gp, html.Div(message_sp,
                                                       style={'font-family': 'Arial', 'font-style': 'italic', 'color': 'red', 'font-size': 16}),
                                "Archivo PDF no generado", None, message_sp)
                    message_ser = "Respuesta generada para punto de interés sin estaciones cercanas representativas."
                    return (resultado_gp,html.Div(message_ser,
                                                  style={'font-family': 'Arial', 'font-style': 'italic', 'color': 'darkorange', 'font-size': 16}),
                            "Certificación tipo oficio lamento sin estaciones cercanas", pdf_path, message_ser)
                
                elif resultado_gp["status"] == "OK":
                    cod_estacion = resultado_gp["message"]
                    estacion_seleccionada = data[data['CODIGO'] == cod_estacion].iloc[0]
                    inicio, fin = construir_rango_fechas(fecha_inicio, fecha_fin)
                    sensor = obtener_sensor(selected_variable)
                    codestacion = construir_codestacion(estacion_seleccionada)

                    conn, cur = create_connection()
                    stationdf = fetch_station_data(cur, inicio, fin, sensor, codestacion)
                    
                    if 'viento' in selected_variable:
                        stationdf['Valor'] = (stationdf['Valor'] * 3.6).round(1)

                    stationdf_fnl = aplicar_transformacion(stationdf, selected_variable)
                    modifdato_LimSup(stationdf_fnl, data, selected_var, selected_variable, codestacion)

                    if selected_variable == "Precipitación total mensual":
                        stationdf_fnl = calculate_indices(stationdf_fnl, normales, codestacion)

                    if selected_variable == "Velocidad del viento horaria":
                        stationdf_dv = fetch_station_data(cur, inicio, fin, 'DVAG_CON', codestacion)
                        stationdf_dv.rename(columns={'Valor': 'Dirección del viento (°)'}, inplace=True)
                        stationdf_fnl = pd.merge(stationdf_fnl, stationdf_dv, on='Fecha')
                    
                    print(stationdf_fnl)
                    # Resultado si no hay datos
                    if stationdf_fnl.empty or stationdf_fnl['Valor'].isna().all():
                        doc = create_certificate_nodata(tpers, nombres, apellidos, correo, fecha_inicio, fecha_fin,
                                                        selected_variable, estacion_seleccionada, descrip_solicit)
                        date_rnow_str = datetime.now().strftime("%Y%m%d_%H%M%S")
                        nombre_archivo_final = f"{date_rnow_str}_{plantillas_por_variable['Sin Datos']}"
                        doc.save(nombre_archivo_final)
                        pdf_path = convertir_a_pdf(nombre_archivo_final)
                        print(f'El path es {pdf_path}')
                        if pdf_path is None:
                            message_sp = "No se pudo generar el archivo PDF"
                            return (resultado_gp, html.Div(message_sp,
                                                        style={'font-family': 'Arial', 'font-style': 'italic', 'color': 'red', 'font-size': 16}),
                                    "Archivo PDF no generado", None, message_sp)
                        message_dnd = "Respuesta generada para punto de interés con estación representativa sin datos disponibles para las fechas seleccionadas."
                        return (resultado_gp,html.Div(message_dnd,
                                                    style={'font-family': 'Arial', 'font-style': 'italic', 'color': 'darkorange', 'font-size': 16}),
                                "Certificación tipo oficio lamento sin datos", pdf_path, message_dnd)

                    doc, nombre_plantilla = select_plantilla(tpers, selected_variable, stationdf_fnl, nombres, apellidos, correo, fecha_inicio, fecha_fin,
                                                             estacion_seleccionada, descrip_solicit)
                    doc = insert_table_in_doc(doc, stationdf_fnl, selected_variable)

                    date_rnow_str = datetime.now().strftime("%Y%m%d_%H%M%S")
                    nombre_archivo_final = f"{date_rnow_str}_{nombre_plantilla}"
                    doc.save(nombre_archivo_final)
                    pdf_path = convertir_a_pdf(nombre_archivo_final)
                    print(f'El path es {pdf_path}')
                    if pdf_path is None:
                        message_sp = "No se pudo generar el archivo PDF"
                        return (resultado_gp, html.Div(message_sp,
                                                       style={'font-family': 'Arial', 'font-style': 'italic', 'color': 'red', 'font-size': 16}),
                                "Archivo PDF no generado", None, message_sp)
                    message_cg = "Se generó la certificación."
                    return (resultado_gp,html.Div(message_cg, style={'font-family': 'Arial', 'font-style': 'italic',
                                                                                        'color': 'green', 'font-size': 16}),
                            "Certificación generada", pdf_path, message_cg)
    
                elif resultado_gp["status"] == "ERROR":
                    mensaje_error = resultado_gp["message"]
                    message_e = f"No se pudo procesar la solicitud,{mensaje_error}"
                    return (resultado_gp, html.Div(message_e,
                                                   style={'font-family': 'Arial', 'font-style': 'italic', 'color': 'darkred', 'font-size': 16}),
                            mensaje_error, None, message_e)
                else:
                    mensaje_faltante = resultado_gp["message"]
                    message_f = f"No se pudo procesar la solicitud,{mensaje_faltante}"
                    return (resultado_gp, html.Div(message_f, 
                                                   style={'font-family': 'Arial', 'font-style': 'italic', 'color': 'darkred', 'font-size': 16}),
                            mensaje_faltante, None, message_f)
                
            except Exception as e:
                error_traceback = traceback.format_exc()
                message_et = f"Intente más tarde, se produjo un error al generar la certificación: {e}"
                return (None, html.Div([html.Div(message_et,
                                          style={'font-family': 'Arial', 'font-style': 'italic', 'color': 'red', 'font-size': 16}),
                                 html.Pre(error_traceback,
                                          style={'font-family': 'Consolas', 'font-style': 'italic', 'color': 'grey', 'font-size': 10})]),
                        None, None, message_et)
        message_click = html.Div("Haga click en el botón de 'Analizar estaciones representativas' para generar la certificación:", 
                               style={'font-family': 'Arial', 'font-style': 'italic', 'font-weight': 'bold', 'font-size': 15})
        return (None, message_click,
                None, None, message_click)
    

    @app.callback(
        Output("esperar-dialog", "displayed"),
        [Input("represanalis-button", "n_clicks"), Input("message-store", "data")]
    )
    def handle_dialog(n_clicks, message):
        # Se extrae solamente el mensaje
        if isinstance(message, dict) and "props" in message:
                message_only = message["props"].get("children", "")
        else:
                message_only = message  # Si el mensaje es un string, usarlo directamente

        # Validar que n_clicks sea un número entero y mayor que 0
        print(f'n_clicks: {n_clicks}, message: {message_only}')
        
        # Se enuncian los posibles mensajes y su tipo
        valid_message = "Haga click en el botón de 'Analizar estaciones representativas' para generar la certificación:"
        invalid_messeges = [
            "Por favor, diligencie completamente el formulario para obtener su certificación.",
            "No se pudo procesar la solicitud,Job failed."
        ]

        # Se hacen las validaciones de cada mensaje
        if n_clicks is not None and message_only == valid_message:
            return True
        elif n_clicks is not None and message_only in invalid_messeges:
            # Extraer el contenido del mensaje
            return False
        elif n_clicks is not None and message_only not in invalid_messeges:
            return True
        
    @app.callback(
        Output("descargar-button", "disabled"),
        [Input("message-store", "data"), Input("represanalis-button", "n_clicks")]
    )
    def update_button(message, n_clicks):
        # Caso 1: Si el mensaje es un diccionario con la clave 'props'
        if isinstance(message, dict) and "props" in message:
            message_only = message["props"].get("children", "")
        else:
            # Caso 2: Si el mensaje es directamente un string
            message_only = message
        #message_only = message["props"]["children"]#.get("props", {}).get("children", "")   
        #print(f"n_clicks: {n_clicks}, message: {message_only}")
        if not message_only or n_clicks is None:
            return True  # No mostrar el diálogo si no hay mensaje o clics

        print(f"n_clicks: {n_clicks}, message: {message}")
        # Definir los mensajes válidos
        valid_states = [
            "Se generó la certificación.",
            "Respuesta generada para punto de interés con estación representativa sin datos disponibles para las fechas seleccionadas.",
            "Respuesta generada para punto de interés sin estaciones cercanas representativas."
        ]

        return message_only not in valid_states
    
    #-----Más funcionales hasta el momento
    # @app.callback(
    #     Output("esperar-dialog", "displayed"),
    #     Input("represanalis-button", "n_clicks"),
    #     State("output-state", "children")
    # )
    # def prompt_dialog(n_clicks, output_state_content):
    #     print("n_clicks:", n_clicks)
    #     print("output_state_content:", output_state_content)
    #     n_clicks = n_clicks or 0
    #     # Extraer el mensaje de output_state_content
    #     if output_state_content is not None:
    #         message = output_state_content.get("props", {}).get("children", "")
    #         print(f"n_clicks: {n_clicks}, message: {message}")

    #         invalidstates = ["Haga click en el botón de 'Analizar...' para generar la certificación:",
    #                          "Por favor, diligencie completamente el formulario para obtener su certificación."]
    #         # Lógica para mostrar el cuadro de diálogo
    #         dialog_displayed = message not in invalidstates 
    #         print(f"Estado del diálogo (mostrar): {dialog_displayed}")
        
    #         return dialog_displayed
    #     else:
    #         return None

    # @app.callback(
    #     Output("descargar-button", "disabled"),
    #     Input("represanalis-button", "n_clicks"),
    #     State("output-state", "children")
    # )
    # def update_button(n_clicks, output_state_content):   
    #     print("n_clicks:", n_clicks)
    #     print("output_state_content:", output_state_content)
    #     #n_clicks = n_clicks or 0
    #     # Extraer el mensaje de output_state_content
    #     if output_state_content is not None:
    #         message = output_state_content.get("props", {}).get("children", "")
    #         print(f"n_clicks: {n_clicks}, message: {message}")

    #         # Definir los mensajes válidos
    #         valid_states = [
    #             "Se generó la certificación.",
    #             "Respuesta generada para punto de interés con estación representativa sin datos disponibles para las fechas seleccionadas.",
    #             "Respuesta generada para punto de interés sin estaciones cercanas representativas."
    #         ]
    #         # Lógica para mostrar el cuadro de diálogo
    #         #button_disabled = n_clicks > 0 and message not in valid_states 
    #         button_disabled = message in valid_states
    #         print(f"Estado del diálogo (mostrar): {button_disabled}")
        
    #         return not button_disabled
    #     else:
    #         return True
    #------Final de más funcionales hasta el momento

    # @app.callback(
    #     Output("descargar-button", "disabled"),
    #     Input("represanalis-button", "n_clicks"),
    #     State("output-state", "children")
    # )
    # def update_button(n_clicks, output_state_content):
    #     print("n_clicks:", n_clicks)
    #     print("output_state_content:", output_state_content)
    #     n_clicks = n_clicks or 0
    #     # Extraer el mensaje de output_state_content
    #     if output_state_content is not None:
    #         message = output_state_content.get("props", {}).get("children", "")
    #         print(f"n_clicks: {n_clicks}, message: {message}")

    #         valid_states = [
    #             "Se generó la certificación.", 
    #             "Respuesta generada para punto de interés con estación representativa sin datos disponibles para las fechas seleccionadas.",
    #             "Respuesta generada para punto de interés sin estaciones cercanas representativas."
    #         ]
    #         # Lógica para habilitar el botón de descarga
    #         button_disabled = message not in valid_states
    #         print(f"Estado del botón de descarga (deshabilitado): {button_disabled}")

    #         return not button_disabled
    #     else:
    #         return None

    @app.callback(
        [Output("saved-information", "children"),
         Output("download-certif", "data")],
        Input("descargar-button", "n_clicks"),
        [State("gp-result-store", "data"),
         State("certtyc-result-store", "data"),
         State("pdf_data", "data"),
         State("tpersona-ri","value"),
         State("tdoc-dp", "value"),
         State("ndoc-input", "value"),
         State("nombres-input", "value"),
         State("apellidos-input", "value"),
         State("correo-input", "value"),
         State("tel-input", "value"),
         State("genero-dp", "value"),
         State("genero-input", "value"),
         State("grupetn-dp", "value"),
         State("grupetn-input", "value"),
         State("infpoblac-dp", "value"),
         State("discap-dp", "value"),
         State("discap-input", "value"),
         State("ginteres-dp", "value"),
         State("ginteres-input", "value"),
         State("variable-dp", "value"),
         State("tiposerie-dp", "value"),
         State("inidate-pckr", "value"),
         State("findate-pckr", "value"),
         State("upload-data", "filename"),
         State("click-info", "children")],
         prevent_initial_call=True
    )
    def guardresults_regsolicit_tb(n_clicks,gpresult,outstate,pdf_path,tpers,tdoc, ndoc, nombres, apell,
                                   corr, tel, gendp, genin, getndp, getnin, infpob, discdp,
                                   discin, gintdp, gintin, vardp, tipsrdp, fecha_inicio, fecha_fin, upld, clickinfo):
        if n_clicks and pdf_path is None:
            pass
        
        update_table = UpdateTable()

        if isinstance(gpresult, dict):
            resultado_status = gpresult.get('status', 'Estado no disponible')
            resultado_message = gpresult.get('message', 'Mensaje no disponible')
        else:
            print(f"gpresult no es un diccionario: {gpresult}")
            resultado_status = "Estado no disponible"
            resultado_message = "Mensaje no disponible"

        if isinstance(outstate, str):
            outstate_str = outstate
        else:
            print(f"outstate no es una cadena: {outstate}")
            outstate_str = "Estado no disponible"

        try:
            # Operador ternario para asignaciones más limpias
            gendp = gendp if gendp else genin
            getndp = getndp if getndp else getnin
            discdp = discdp if discdp else discin
            gintdp = gintdp if gintdp else gintin

            if upld is None:
                coord = clickinfo
                x = coord[1]
                y = coord[0]
                coord_s = (coord[0],coord[1])
                coord_str = str(coord_s)
                print(coord)
            else:
                print(upld)
                coordenadas = update_table.obtener_coordenadas_zip(os.path.join(UPLOAD_DIRECTORY, upld))
                extract_coords = (coordenadas[0][1],coordenadas[0][0])
                coord_str = str(extract_coords)
                x = coordenadas[0][0]
                y = coordenadas[0][1]

            # Fecha y hora actuales en la zona horaria local ## Es correspondiente y no es necesario
            # cambiar la Timezone
            date_now = datetime.now()

            data_list = [
                {
                    "tpersona_ri": tpers,
                    "tdoc_dp": tdoc,
                    "ndoc_input": ndoc,
                    "nombres_input": nombres,
                    "apellidos_in": apell,
                    "correo_input": corr,
                    "tel_input": tel,
                    "genero_dp": gendp,
                    "genero_input": gendp,
                    "grupetn_dp": getndp,
                    "grupetn_input": getndp,
                    "infpoblac_dp": infpob,
                    "discap_dp": discdp,
                    "discap_input": discdp,
                    "ginteres_dp": gintdp,
                    "ginteres_input": gintdp,
                    "variable_dp": vardp,
                    "tiposerie_dp": tipsrdp,
                    "inidate_pckr": fecha_inicio,
                    "findate_pckr": fecha_fin,
                    "upload_zip_click_info": coord_str,
                    "resultado_status_": resultado_status,
                    "resultado_message_": resultado_message,
                    "output_state": outstate_str,
                    "date_displ": date_now,
                    "geometry": {
                        "x": x,
                        "y": y,
                        "spatialReference": {"wkid": 4326}
                        }
                }]
            
            result = update_table.actualizar_tabla(data_list)
            print("Intentando subir los siguientes datos:", data_list)
            print("Resultado de la actualización de la tabla:", result)

            return ("Datos guardados exitosamente", dcc.send_file(pdf_path))
        except Exception as e:
            print(f"Error en el proceso de cargue de datos: {e}")
            return (None, None)
        
    @app.callback(
        Output('esperarpdf-dialog', 'displayed'),
        Input('descargar-button', 'n_clicks')
    )
    def show_pdf_dialog(n_clicks):
        if n_clicks:
            return True  # Muestra el diálogo
        return False  # No muestra el diálogo
    