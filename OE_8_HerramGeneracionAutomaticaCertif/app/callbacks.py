import dash
import plotly.express as px
import dash_leaflet as dl
import base64
import os
import pytz
import json
import traceback
import sys
import pythoncom
import io
import time
#from docs.replace_data import reemplazar_datos_noEMC, reemplazar_datos_nan, reemplazar_datos_precip, reemplazar_datos
from dash import html, dcc
from datetime import datetime, timedelta, timezone
from dash.dependencies import Input, Output, State
from docs.generate_docs import create_certificate, create_certificate_no_station, select_plantilla, insert_table_in_doc
from utils.helpers import * #(obtener_sensor, construir_rango_fechas, construir_codestacion, 
                           #construir_descripsolicit, fetch_station_data, aplicar_transformacion, 
                           #modifdfprecip_ClasifLimSup, get_normal_value, calculate_indices, 
                           #set_und, calculate_distance)
from utils.db_connection import create_connection
from utils.validation import validate_inputs
from docx import Document
from docx2pdf import convert
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
            return "Haga click en el mapa para obtener las coordenadas de su punto de interés"
        print(f"Las coordenadas seleccinadas fueron: {click_lat_lng}") # Ver en consola las coordenadas seleccionadas
        
        coordenadas = (click_lat_lng["latlng"]["lat"], click_lat_lng["latlng"]["lng"])
        return coordenadas

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

    # # Variable global para almacenar el archivo PDF generado
    # @app.callback(
    #     [Output("output-state", "children"),
    #      Output("download-certif", "data")],
    #     [Input("generar-button", "n_clicks"), 
    #      Input("descargar-button", "n_clicks")],
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

    # def generar_certificado(n_clicks, n_clicks2, nombres, apellidos, correo, dias, meses, ano, selected_variable, estacion_nombre):#, sin_estacion, lat, lon):

                # ...Todo el resto del código...
    #             nombre_archivo_final = f"Modif_{nombre_plantilla}"
    #             doc.save(nombre_archivo_final)
    #             # Se espera 1 segundo para asegurarse de que el archivo se haya guardado completamente
    #             time.sleep(1)
    #             if os.path.exists(nombre_archivo_final):
    #                 # Inicializa COM
    #                 try: 
    #                     pythoncom.CoInitialize()
    #                     pdf_path = f'{nombre_archivo_final[:-5]}.pdf'
    #                     convert(nombre_archivo_final, pdf_path)
    #                     # Guardar el archivo PDF en un buffer
    #                     buffer = io.BytesIO()
    #                     with open(pdf_path, 'rb') as f:
    #                         buffer.write(f.read())
    #                     buffer.seek(0)
    #                     archivo_pdf_generado = buffer.read()

    #                     return (html.Div("Se generó la certificación. Ahora puede descargarla en formato PDF.",
    #                                 style={'font-family': 'Arial', 'font-style': 'italic', 'color': 'darkgreen', 'font-size': 13}),
    #                         None)
    #                 except Exception as e:
    #                     return (html.Div(f"Error durante la conversión a PDF: {e}",
    #                                 style={'font-family': 'Arial', 'font-style': 'italic', 'color': 'red', 'font-size': 13}),
    #                         None)
    #                 finally:
    #                     # Liberar COM
    #                     pythoncom.CoUninitialize()
    #             else:
    #                 return (html.Div("Error: El archivo no se generó correctamente.",
    #                             style={'font-family': 'Arial', 'font-style': 'italic', 'color': 'red', 'font-size': 13}),
    #                     None)
    #         except Exception as e:
    #             error_traceback = traceback.format_exc()
    #             return (html.Div([html.Div(f"Error al generar la certificación: {e}",
    #                                   style={'font-family': 'Arial', 'font-style': 'italic', 'color': 'red', 'font-size': 13}),
    #                          html.Pre(error_traceback,
    #                                   style={'font-family': 'Consolas', 'font-style': 'italic', 'color': 'grey', 'font-size': 10})]), None)

    #     # Lógica para descargar el certificado cuando se presiona el botón "Descargar"
    #     elif n_clicks is None and n_clicks2 is None:
    #         return (html.Div("Haga clic en este botón para generar la certificación:",
    #                         style={'font-family': 'Arial', 'font-style': 'italic', 'font-weight': 'bold', 'font-size': 13}),
    #                 None)

    #     # Lógica de descarga del certificado
    #     if n_clicks2: #and archivo_pdf_generado:
    #         return (None, dcc.send_bytes(archivo_pdf_generado, "certificacion.pdf"))

    #     return (None, None)
    
    @app.callback(
        [Output("gp-result-store", "data"), #Output("output-represanalis", "children"),
         Output("output-state", "children"),
         Output("certtyc-result-store", "data")],
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
    )

    def generar_certificado(n_clicks, itemid_file, nombres, apellidos, correo, dias, meses, ano, selected_var, selected_variable, upld, clickinfo):#, estacion_nombre, sin_estacion, lat, lon):
        if n_clicks is not None:
            try:
                # Verificar que los campos obligatorios siempre estén llenos
                if not (nombres and apellidos and correo and selected_variable ): #and estacion_nombre):
                    return (None, html.Div("Por favor, diligencie completamente el formulario para obtener su certificación.",
                                           style={'font-family': 'Arial', 'font-style': 'italic', 'color': 'darkred', 'font-size': 13}),
                            None)

                # Validar fechas según la periodicidad seleccionada
                if (('anual' in selected_variable.lower() and not ano) or
                    ('mensual' in selected_variable.lower() and not (meses and ano)) or
                    ('diaria' in selected_variable.lower() and not (dias and meses and ano))):
                    return (None, html.Div("Por favor, seleccione las fechas correspondientes para obtener su certificación.",
                                           style={'font-family': 'Arial', 'font-style': 'italic', 'color': 'darkred', 'font-size': 13}),
                            None)

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
                    doc = create_certificate_no_station(nombres, apellidos, correo, descrip_solicit, clickinfo)
                    nombre_archivo_final = f"Modif_{plantillas_por_variable['Sin Estación']}"
                    doc.save(nombre_archivo_final)
                    return (resultado_gp,html.Div("Respuesta generada para punto de interés sin estaciones cercanas representativas.",
                                                  style={'font-family': 'Arial', 'font-style': 'italic', 'color': 'darkorange', 'font-size': 13}),
                            "Certificación tipo oficio lamento sin estaciones cercanas")
                
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
                    return (resultado_gp,html.Div("Se generó la certificación.", style={'font-family': 'Arial', 'font-style': 'italic', 'color': 'darkgreen', 'font-size': 13}),
                            "Certificación generada")
                
                elif resultado_gp["status"] == "ERROR":
                    mensaje_error = resultado_gp["message"]
                    return (resultado_gp, html.Div(f"No se pudo procesar la solicitud,{mensaje_error}",
                                                   style={'font-family': 'Arial', 'font-style': 'italic', 'color': 'darkred', 'font-size': 13}),
                            mensaje_error)
                else:
                    mensaje_faltante = resultado_gp["message"]
                    return (resultado_gp, html.Div(f"No se pudo procesar la solicitud,{mensaje_faltante}", 
                                                   style={'font-family': 'Arial', 'font-style': 'italic', 'color': 'darkred', 'font-size': 13}),
                            mensaje_faltante)
                
            except Exception as e:
                error_traceback = traceback.format_exc()
                return (None, html.Div([html.Div(f"Intente más tarde, se produjo un error al generar la certificación: {e}",
                                          style={'font-family': 'Arial', 'font-style': 'italic', 'color': 'red', 'font-size': 13}),
                                 html.Pre(error_traceback,
                                          style={'font-family': 'Consolas', 'font-style': 'italic', 'color': 'grey', 'font-size': 10})]),
                        None)
        return (None, html.Div("Haga clic en este botón para generar la certificación:", 
                               style={'font-family': 'Arial', 'font-style': 'italic', 'font-weight': 'bold', 'font-size': 13}),
                None)
    
    @app.callback(
        Output('esperar-dialog', 'displayed'),
        Input('represanalis-button', 'n_clicks')
    )
    def show_confirm_dialog(n_clicks):
        if n_clicks:
            return True  # Muestra el diálogo
        return False  # No muestra el diálogo

    @app.callback(
        Output("saved-information", "children"),
        Input("descargar-button", "n_clicks"),
        # [Input("descargar-button", "n_clicks"),
        #  Input("gp-result-store", "data"),
        #  Input("certtyc-result-store", "data")],
        [State("gp-result-store", "data"),
         State("certtyc-result-store", "data"),
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
         State("dias-dropdown", "value"),
         State("meses-dropdown", "value"),
         State("ano-dropdown", "value"),
         State("upload-data", "filename"),
         State("click-info", "children")]
    )
    def guardresults_regsolicit_tb(n_clicks,gpresult,outstate,tpers,tdoc, ndoc, nombres, apell,
                                   corr, tel, gendp, genin, getndp, getnin, infpob, discdp,
                                   discin, gintdp, gintin, vardp, tipsrdp, dia, mes, ano, upld, clickinfo):
        if n_clicks is None:
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
                    "dias_dropdown": dia,
                    "meses_dropdown": mes,
                    "ano_dropdown": ano,
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

            return "Datos guardados exitosamente"
        except Exception as e:
            print(f"Error en el proceso de cargue de datos: {e}")