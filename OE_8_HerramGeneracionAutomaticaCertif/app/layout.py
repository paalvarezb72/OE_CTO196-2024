# app/layout.py
from dash import html, dcc
import pandas as pd
import dash_leaflet as dl
from arcgis.gis import GIS
from arcgis.mapping import WebMap
from arcgis.features import FeatureLayer

gis = GIS("https://visualizador.ideam.gov.co/portal", "GDRM_IDEAM", "Meteo2024.")

# Obtén el WebMap de ArcGIS Online
webmap_item = gis.content.get("8ac9fc5932e74b07b2c5b0d6be3eec8e")
webmap = WebMap(webmap_item)

# Se extraen las capas del WebMap
layers = []
for layer in webmap.layers:
    layers.append(dl.TileLayer(url=layer.url))
    print(layer.url)

def create_layout(app, data):
    # Se define la estructura de la página web
    layout = html.Div([
        # Banner
        html.Div(
            id="banner",
            className="banner",
            children=[
                # Contenedor para la imagen superior
                html.Div([
                    html.Img(src=app.get_asset_url('Banner_GovCo.png'), style={
                            'width': '100%', 'display': 'block', 'margin-top': '0', 'padding-top': '0'}),
                    html.Div([
                        html.A("Ir a GovCo", href="https://www.gov.co/", target="_blank",
                               style={'color': 'white', 'text-decoration': 'underline'}),
                    ], style={
                        'position': 'absolute', 'right': '10px', 'bottom': '10px', 
                        'padding': '5px','border-radius': '5px'
                    }),
                ], style={'width': '100%', 'display': 'block', 'margin-top': '0', 'padding-top': '0'}),
            ]
        ),
        
        # Espaciador
        html.Div(style={'height': '50px', 'width': '100%'}),

        # Contenedor para el logo
        html.Div([
            html.Img(src=app.get_asset_url('Logo_IDEAM_Color2.png'), style={
                    'display': 'inline-block', 'width': 'auto'}),
        ], style={'margin-left': '5%', 'margin-right': '5%','width': '100%', 'display': 'flex',
                  'justify-content': 'space-between', 'align-items': 'center'}),

        html.Div(style={'height': '10px', 'width': '100%'}),

        # Contenedor del resto de contenidos
        html.Div(
            # Ajusta los márgenes según necesites
            style={'margin-left': '5%', 'margin-right': '5%'},
            children=[
                html.H1("Certificaciones del estado del tiempo y clima", 
                        style={'font-family': 'arial', 'text-align': 'center'}, #, 'font-weight': 'bold'
                        title="Datos obtenidos de la red de observación en superficie IDEAM "),
                # Espaciador
                html.Div(style={'height': '10px', 'width': '100%'}),
                html.P("Instrucciones:", style={'font-family': 'arial', 'text-align': 'justify','font-size': 11,
                                                'font-weight': 'bold', 'margin-bottom': '5px'}),
                html.P("Respetado usuario, en esta aplicación podrá obtener certificaciones del estado del tiempo;\
                        para ello se solicitarán datos sus personales, de contacto, variable meteorológica y periodo de\
                        interés, así como las fechas requeridas y ubicación del punto de interés; por lo cual, antes de\
                        empezar, es importante que conozca esta información pues su certificación estará basada en ella.\
                        Recuerde que puede disponer del shape completo (archivos .cpg, .dbf, .prj, .sbn, .sbx, .shp, .shx)\
                        comprimidos en .zip para ubicar su punto de interés o saber donde ubicarlo haciendo click en el\
                        mapa más adelante.",
                        style={'font-family': 'arial', 'text-align': 'justify', 'margin-bottom': '20px',
                               'font-size': 11}),
                html.P(["Por favor, diligiencie todos los campos para obtener su certificación. Tenga\
                       en cuenta la ",
                       dcc.Link("política de tratamiento y protección de datos personales.",
                                href="https://www.ideam.gov.co/sites/default/files/archivos/politica_de_tratamiento_y_proteccion_de_datos_personales_0.pdf",
                                target="_blank")],
                       style={'text-align': 'justify', 'margin-bottom': '20px', 'font-weight': 'bold'}), #'font-family': 'arial', 
                html.Div([
                    html.P("Datos personales:", style={'font-family': 'arial', 'text-align': 'center',
                                                       'font-weight': 'bold', 'font-size': 13}),
                ], style={'display': 'flex', 'justify-content': 'space-between', 'flex-wrap': 'wrap'}),
                html.Div([
                    html.Div([
                        html.Label("Tipo solicitante:", style={
                            'font-family': 'arial', 'color': '#5D5D5D', 'font-size': 13, 'width': '100%'}),
                        dcc.RadioItems(['Persona natural', 'Persona jurídica'], value='Persona natural', id="tpersona-ri",
                                        labelStyle={'display': 'inline-block', 'margin-right': '10px'}),
                    ], style={'flex': 1, 'padding': '0 6px', 'font-size': 12}),

                    html.Div([
                        html.Label("Tipo de documento:", style={
                            'font-family': 'arial', 'color': '#5D5D5D', 'font-size': 13, 'width': '100%'}),
                        dcc.Dropdown(['Cédula de ciudadanía', 'NIT', 'Tarjeta de identidad', 'Cédula de extranjería',
                                    'Pasaporte', 'Permiso especial de permanencia - PEP',
                                    'Permiso de protección temporal - PPT'], value='Cédula de ciudadanía', id="tdoc-dp"),
                    ], style={'flex': '1', 'padding': '0 6px', 'font-size': 12}),                                               
                    html.Div([
                        html.Label("Número de documento:", style={
                            'font-family': 'arial', 'color': '#5D5D5D', 'font-size': 13, 'width': '100%'}),
                        dcc.Input(id="ndoc-input", type="number", placeholder='1234567890', maxLength=10,
                                  style={'width': '100%'}),
                    ], style={'flex': 1, 'padding': '0 10px', 'min-width': '70px'}),
                    html.Div([
                        html.Label("Nombre(s) o razón social:", style={
                            'font-family': 'arial', 'color': '#5D5D5D', 'font-size': 13, 'width': '100%'}),
                        dcc.Input(id="nombres-input", type="text", placeholder='Digite su(s) nombre(s)',
                                  style={'width': '100%'}),
                    ], style={'flex': 1, 'padding': '0 10px', 'min-width': '180px'}),            
                ], style={'display': 'flex', 'justify-content': 'space-between', 'flex-wrap': 'wrap'}),
                #html.Div([
                    
                html.Div([
                    html.Div([
                        html.Label("Apellido(s):", style={
                            'font-family': 'arial', 'color': '#5D5D5D', 'font-size': 13, 'width': '100%'}),
                        dcc.Input(id="apellidos-input", type="text", placeholder='Digite su(s) apellido(s)',
                                  style={'width': '100%'}), #, 'min-width': '80px'
                    ], style={'flex': 1, 'padding': '0 10px', 'min-width': '180px'}), 
                    html.Div([
                        html.Label("Género:", style={
                            'font-family': 'arial', 'color': '#5D5D5D', 'font-size': 13, 'width': '100%'}),
                        dcc.Dropdown(['Femenino', 'Masculino', 'No deseo registrar esta información', 'Otro'], 
                                    value='Femenino', id="genero-dp"),
                        html.Label("¿Cuál?", style={
                            'font-family': 'arial', 'color': '#5D5D5D', 'font-size': 13}),
                        dcc.Input(id="genero-input", type="text", placeholder='Digite el género'),
                    ], style={'flex': '1', 'padding': '0 6px', 'width': '180px', 'font-size': 12}),
                    html.Div([
                        html.Label("Grupo étnico:", style={
                                'font-family': 'arial', 'color': '#5D5D5D', 'font-size': 13}),
                        dcc.Dropdown(['Indígena', 'Gitano (rom)', 'Negro, mulato, afrodescendiente, afrocolombiano, raizal o Palenquero',
                                  'Otro','Ninguno'], value='Indígena', id="grupetn-dp"),
                        html.Label("¿Cuál?", style={
                                'font-family': 'arial', 'color': '#5D5D5D', 'font-size': 13}),
                        dcc.Input(id="grupetn-input", type="text", placeholder='Digite el grupo étnico'),
                    ], style={'flex': 1, 'padding': '0 10px', 'min-width': '80px', 'font-size': 12}),
                ], style={'display': 'flex', 'justify-content': 'space-between', 'flex-wrap': 'wrap'}),
                                # Espaciador
                html.Div(style={'height': '10px', 'width': '100%'}),
                # Contenedor resto de información personal
                html.Div([                   
                    html.Div([
                        html.Label("Información poblacional:", style={
                                'font-family': 'arial', 'color': '#5D5D5D', 'font-size': 13}),
                        dcc.Dropdown(['Niños, Niñas y Adolescentes', 'Adulto Mayor', 'Mujer cabeza de familia',
                                      'Personas en condición de discapacidad', 'Población LGBTIQ+',
                                      'Personas desplazadas por la violencia y aquellas que se encuentran en pobreza extrema',
                                      'Ninguno'], value='Niños, Niñas y Adolescentes', id="infpoblac-dp"),
                    ], style={'flex': 1, 'padding': '0 10px', 'min-width': '80px', 'font-size': 12}),

                    html.Div([
                        html.Label("¿Presenta discapacidad?", style={
                                'font-family': 'arial', 'color': '#5D5D5D', 'font-size': 13}),
                        dcc.Dropdown(['Física', 'Auditiva', 'Visual','Sordoceguera', 'Intelectual – Cognitiva',
                                      'Psicosocial', 'Talla baja','Otra','Ninguna'], value='Física', id="discap-dp"),
                        html.Label("¿Cuál?", style={
                                'font-family': 'arial', 'color': '#5D5D5D', 'font-size': 13}),
                        dcc.Input(id="discap-input", type="text", placeholder='Digite el grupo étnico'),
                    ], style={'flex': 1, 'padding': '0 10px', 'min-width': '80px', 'font-size': 12}),

                    html.Div([
                        html.Label("Grupo de interés:", style={
                                'font-family': 'arial', 'color': '#5D5D5D', 'font-size': 13}),
                        dcc.Dropdown(['Ciudadano', 'Empresa privada', 'Academia','Ente de control', 'Medio de comunicación',
                                      'Extranjero', 'Entidad pública','Organismo internacional', 'Usuario interno o colaborador',
                                      'Otro'], 
                                      value='Ciudadano', id="ginteres-dp"),
                        html.Label("¿Cuál?", style={
                                'font-family': 'arial', 'color': '#5D5D5D', 'font-size': 13}),
                        dcc.Input(id="ginteres-input", type="text", placeholder='Digite el grupo étnico'),
                    ], style={'flex': 1, 'padding': '0 10px', 'min-width': '80px', 'font-size': 12}),                   
                ], style={'display': 'flex', 'justify-content': 'flex-start', 'flex-wrap': 'wrap'}),

                # Espaciador
                html.Div(style={'height': '10px', 'width': '100%'}),
                html.Div(
                    html.P("Datos de contacto:",
                            style={'font-family': 'arial', 'text-align': 'justify', 'font-weight': 'bold',
                                   'font-size': 13}),
                ),
                html.Div([
                    html.Div([
                        html.Label("Correo:", style={
                                'font-family': 'arial', 'color': '#5D5D5D', 'font-size': 13}),
                        dcc.Input(id="correo-input", type="email", placeholder='ejemplo@dominio.com',
                                  style={'width': '100%'}),
                    ], style={'flex': 1, 'padding': '0 10px', 'min-width': '70px'}),

                    html.Div([
                        html.Label("Teléfono de contacto:", style={
                                'font-family': 'arial', 'color': '#5D5D5D', 'font-size': 13}),
                        dcc.Input(id="tel-input", type="number", placeholder='3124567890',style={'width': '100%'}),
                    ], style={'flex': 1, 'padding': '0 10px', 'min-width': '70px'}),
                    # Div sección columna 3 datos contacto
                    html.Div([
                        # Espacio en blanco
                    ], style={'flex': 1, 'padding': '0 10px', 'min-width': '70px'}),
                ], style={'display': 'flex', 'justify-content': 'space-between', 'flex-wrap': 'wrap'}),                  
                # Espaciador
                html.Div(style={'height': '20px', 'width': '100%'}),
                # Texto intermedio
                html.Div(
                    html.P("Por favor, elija la variable meteorológica y su periodicidad de interés:",
                        style={'font-family': 'arial', 'text-align': 'justify', 'margin-bottom': '20px'}),
                    style={'height': '20px', 'width': '100%'}),

                # Espaciador
                html.Div(style={'height': '15px', 'width': '100%'}),

                # Sección de escoger la variable y su temporalidad
                html.Div([
                    html.Div([
                        html.Label("Variable meteorológica:", style={
                                'font-family': 'arial', 'color': '#5D5D5D', 'font-size': 13}),
                        dcc.Dropdown(
                            id="variable-dp",
                            options=[
                                {"label": "Precipitación", "value": "Precipitación"},
                                {"label": "Temperatura máxima",
                                    "value": "Temperatura máxima"},
                                {"label": "Temperatura mínima",
                                    "value": "Temperatura mínima"},
                                {"label": "Temperatura del aire",
                                    "value": "Temperatura del aire"},
                                {"label": "Velocidad del viento", "value": "Velocidad del viento"}],
                            style={'font-family': 'arial'}
                        ),
                    ], style={'flex': 1, 'padding': '0 10px', 'min-width': '300px'}),

                    html.Div([
                        html.Label("Variable y periodo:", style={
                                'font-family': 'arial', 'color': '#5D5D5D', 'font-size': 13}),
                        dcc.Dropdown(id="tiposerie-dp",
                                    style={'font-family': 'arial'})
                    ], style={'flex': 1, 'padding': '0 10px', 'min-width': '300px'}),

                ], style={'display': 'flex', 'justify-content': 'space-between', 'flex-wrap': 'wrap'}),

                # Espaciador
                html.Div(style={'height': '20px', 'width': '100%'}),

                html.P("Por favor, escoja las fechas de interés para su certificación. Si  requiere\
                    un rango, seleccione solo los días/meses/años de a la fecha inicial y final:",
                    style={'font-family': 'arial', 'text-align': 'justify', 'margin-bottom': '20px'}),

                html.Div([
                    html.Div([
                        html.Label("Día(s):", style={
                                'font-family': 'arial', 'color': '#5D5D5D', 'font-size': 13}),
                        dcc.Dropdown(
                            id="dias-dropdown",
                            options=[{"label": str(i), "value": i}
                                    for i in range(1, 32)],
                            multi=True,
                            # Ajusta el ancho del dropdown al 100% del contenedor
                            style={'width': '100%', 'font-family': 'arial'}
                        ),
                    ], style={'flex': 1, 'padding': '0 10px', 'min-width': '300px'}),  # Ajusta el padding para espacio interno y un min-width

                    html.Div([
                        html.Label("Mes(es):", style={
                                'font-family': 'arial', 'color': '#5D5D5D', 'font-size': 13}),
                        dcc.Dropdown(
                            id="meses-dropdown",
                            options=[
                                {"label": "Enero", "value": "enero"}, {
                                    "label": "Febrero", "value": "febrero"},
                                {"label": "Marzo", "value": "marzo"}, {
                                    "label": "Abril", "value": "abril"},
                                {"label": "Mayo", "value": "mayo"}, {
                                    "label": "Junio", "value": "junio"},
                                {"label": "Julio", "value": "julio"}, {
                                    "label": "Agosto", "value": "agosto"},
                                {"label": "Septiembre", "value": "septiembre"}, {
                                    "label": "Octubre", "value": "octubre"},
                                {"label": "Noviembre", "value": "noviembre"}, {
                                    "label": "Diciembre", "value": "diciembre"}
                            ],
                            multi=True,
                            # Igual aquí
                            style={'width': '100%', 'font-family': 'arial'}
                        ),
                    ], style={'flex': 1, 'padding': '0 10px', 'min-width': '300px'}),  # Y aquí

                    html.Div([
                        html.Label("Año(s):", style={
                                'font-family': 'arial', 'color': '#5D5D5D', 'font-size': 13}),
                        dcc.Dropdown(
                            id="ano-dropdown",
                            options=[{"label": str(i), "value": i}
                                    for i in range(2024, 1949, -1)],
                            multi=True,
                            # Y finalmente aquí
                            style={'width': '100%', 'font-family': 'arial'}
                        ),
                    ], style={'flex': 1, 'padding': '0 10px', 'min-width': '300px'})
                ], style={'display': 'flex', 'justify-content': 'space-between', 'flex-wrap': 'wrap'}), 

                # Espaciador
                html.Div(style={'height': '30px', 'width': '100%'}),

                html.H5("Información geográfica de su punto de interés: cargue la geometría o haga click en el mapa", 
                        style={'font-family': 'arial', 'text-align': 'left'}, #, 'font-weight': 'bold'
                        title="Inicio módulo geográfico de la aplicación"),

                # Espaciador
                html.Div(style={'height': '20px', 'width': '100%'}),

                html.P("En esta caja, cargue en formato .zip la geometría tipo punto (un solo punto) de\
                        su sitio de interés. Recuerde incluir en la carpeta comprimida todos los archivos\
                        que acompañan el .shp (.cpg, .dbf, .prj, .sbn, .sbx, .shx)",
                    style={'font-family': 'arial', 'text-align': 'justify', 'margin-bottom': '20px'}),

                html.Div([
                    dcc.Upload(
                        id='upload-data',
                        children=html.Div([
                            'Arrastre y suelte su archivo .zip o ',
                            html.A('selecciónelo desde su ordenador')
                        ]),
                        style={
                            'width': '100%',
                            'height': '60px',
                            'lineHeight': '60px',
                            'borderWidth': '1px',
                            'borderStyle': 'dashed',
                            'borderRadius': '5px',
                            'textAlign': 'center',
                            'margin': '10px'
                        },
                        accept='.zip'
                    ),
                    html.Div(id='upload-status'),
                    dcc.Store(id='file-storage', storage_type='session'), 
                ]),

                # Espaciador
                html.Div(style={'height': '20px', 'width': '100%'}),

                html.P("Las coordenadas que seleccionó de su punto de interés son:",
                    style={'font-family': 'arial', 'text-align': 'justify', 'margin-bottom': '5px'}),

                html.Div([
                    html.Div(id="click-info"),  # Div para mostrar la información del clic
                    dl.Map(center=[4, -74], zoom=10, 
                        children=[
                            dl.TileLayer(),  # Capa base
                            #dl.LayerGroup(markers),
                            dl.LayerGroup([
                            dl.CircleMarker(center=[row['latitud'], row['longitud']], 
                                            radius=2, color='blue', fill=True, 
                                            children=[dl.Tooltip(f"Nombre: {row['nombre']}, Altitud: {row['altitudDEM']} m")
                                                      ]) for i, row in data.iterrows()]),
                            dl.LayerGroup(id="click-layer")  # Capa para los clics
                        ], 
                        style={'width': '100%', 'height': '70vh'}, id="map"),
                ]),

                # Espaciador
                html.Div(style={'height': '20px', 'width': '100%'}),

                html.P("Haga click en el botón 'Analizar estaciones representativas' para ejecutar el análisis\
                        de representatividad de estaciones meteorológicas. Una vez se encuentre la estación más\
                        representativa, el sistema generará su certificación.",
                    style={'font-family': 'arial', 'text-align': 'justify', 'margin-bottom': '10px'}),

                html.P("Oprima el botón 'Descargar certificación' solo cuando el mensaje de encima de los botones\
                       haya cambiado a uno de color verde o naranja.",
                    style={'font-family': 'arial', 'text-align': 'justify', 'margin-bottom': '20px', 'font-weight': 'bold',
                           'font-size': 13}),

                dcc.Store(id='gp-result-store'),
                html.Div(id="output-represanalis"),

                dcc.Store(id='certtyc-result-store'),
                html.Div(id='output-state'),
                
                html.Div([
                    html.Button("Analizar estaciones representativas", style={
                            'font-family': 'arial'}, id="represanalis-button"),
                    html.Button("Descargar certificación", id="descargar-button"),
                    dcc.Download(id="download-certif")
                ]),

                dcc.Store(id="pdf_data"),
                
                # Espaciador
                html.Div(style={'height': '20px', 'width': '100%'}),
                
                dcc.ConfirmDialog(
                    id='esperar-dialog',
                    message='Por favor, espere mientras su certificación se genera, no refresque la página.\
                        \n Encima del botón de Análisis usted verá el mensaje correspondiente; oprima luego "Descargar certificación".',
                    ),

                dcc.ConfirmDialog(
                    id='esperarpdf-dialog',
                    message='Por favor, espere mientras se descarga su certificación. No refresque la página',
                    ),
                       
                # Espaciador
                html.Div(style={'height': '20px', 'width': '100%'}),
                # html.Div([
                #     html.Button("Generar Certificación", style={
                #             'font-family': 'arial'}, id="generar-button"),
                #     html.Button("Descargar certificación", id="descargar2-button"),
                #     dcc.Download(id="download-certif")
                # ]),

                # html.Div(style={'height': '10px', 'width': '100%'}),

                html.P([
                    "Al generar su certificación, usted acepta la política tratamiento y protección de datos personales, la cual, puede consultar en ",
                    dcc.Link("este enlace", href="https://www.ideam.gov.co/sites/default/files/archivos/politica_de_tratamiento_y_proteccion_de_datos_personales.pdf", 
                             target="_blank"),"."
                ], style={'font-family': 'arial', 'text-align': 'justify', 'margin-bottom': '20px'}),

                html.P(["Si requiere una certificación con información adicional -fenómenos, anomalías,\
                        análisis climatológicos, entre otros-, por favor tramite su solicitud al correo electrónico ",
                        html.A("contacto@ideam.gov.co", href="mailto:contacto@ideam.gov.co")," o a través del siguiente enlace: ",
                        dcc.Link("Formulario web", href="http://sgdorfeo.ideam.gov.co/orfeo-6.1/formularioWeb/", target="_blank"),"."
                ], style={'font-family': 'arial', 'text-align': 'justify', 'margin-bottom': '20px'}),

                # Espaciador
                html.Div(style={'height': '20px', 'width': '100%'}),

                # Guardado de información
                html.Div(id='saved-information')

            ]),

        html.Footer([
            html.Div([
                html.Div([
                    html.H4("Instituto de Hidrología, Meteorología y Estudios Ambientales"),
                    html.P("Sede principal"),
                    html.P("Dirección ventanilla única de radicación: Calle 25 D No. 96 B - 70 Bogotá D.C."),
                    html.P("Código Postal: 110911"),
                    html.P("Horario de atención: Lunes a Viernes 8:00 am - 5:00 pm"),
                    html.P("PBX: +57 (601) 352 7160"),
                    html.P("Pronóstico y Alertas: +57 (601) 307 5625"),
                    html.P("Línea gratuita nacional: 01 8000 110012"),
                    html.P([
                        "Línea anticorrupción: ",
                        html.A("denunciacorrupcion@ideam.gov.co", href="mailto:denunciacorrupcion@ideam.gov.co")
                    ]),
                    html.P([
                        "Dirección electrónica exclusiva para notificaciones judiciales al IDEAM: ",
                        html.A("notificacionesjudiciales@ideam.gov.co", href="mailto:notificacionesjudiciales@ideam.gov.co")
                    ]),
                    html.P([
                        "Radicación de comunicaciones oficiales vía web: ",
                        html.A("contacto@ideam.gov.co", href="mailto:contacto@ideam.gov.co")
                    ]),
                    html.Div([
                        html.A(html.Img(src="/assets/logofb.png",alt="Facebook",style={'max-height': '30px'}), 
                               href="https://www.facebook.com/ideam.instituto", target="_blank"),html.P('Facebook'),
                        html.A(html.Img(src="/assets/logoIG.png", alt="Instagram",style={'max-height': '30px'}), 
                               href="https://www.instagram.com/ideamcolombia/", target="_blank"),html.P('Instagram'),
                        html.A(html.Img(src="/assets/logoX.png", alt="X",style={'max-height': '30px'}), 
                               href="https://x.com/IDEAMColombia", target="_blank"),html.P('X'),
                        html.A(html.Img(src="/assets/logoYT.png", alt="YouTube",style={'max-height': '30px'}), 
                               href="https://www.youtube.com/user/InstitutoIDEAM", target="_blank"),html.P('YouTube'),
                    ], style={'display': 'flex', 'gap': '10px', 'margin-top': '10px'}),
                    # Espaciador
                    html.Div(style={'height': '50px', 'width': '100%'}),
                    html.Div([
                        html.A("Políticas", href="https://www.ideam.gov.co/politica-de-tratamiento-de-datos", 
                               target="_blank", style={'width': '100%'}),
                        html.A("Mapa del sitio", href="https://www.ideam.gov.co/", target="_blank", style={'width': '100%'}),
                        html.A("Términos y condiciones", href="https://www.ideam.gov.co/", target="_blank",
                               style={'width': '100%'}),
                        html.A("Accesibilidad", href="https://ideam.gov.co/accesibilidad", target="_blank",
                               style={'width': '100%'}),
                    ], style={'display': 'flex', 'justify-content': 'space-between', 'gap': '20px'}),
                ], className='footer-left'),
                html.Div([
                    html.Img(src="/assets/LOGO_AMBIENTE_2024.png", alt="Ambiente", style={'height': '300px'}), 
                ], className='footer-right')
            ], className='footer-container'),
        ], className='footer',style={'width': '100%', 'max-width': '1200px', 'margin': '0 auto'}),
        # Banner afuera del contenedor
        html.Div([
            html.Img(src=app.get_asset_url('Banner_GovCo_Bottom.png'), style={
                        'width': '100%', 'display': 'block', 'margin': '0', 'padding': '0'}),
        ], className='footer-bottom', style={'width': '100%', 'position': 'relative', 'bottom': '0'}),

        ], style={'width': '100%', 'max-width': '1200px', 'margin': '0 auto'})
    
    # app.css.append_css({
    #     'external_url': 'https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css'
    # })

    # app.css.append_css({
    #     'external_url': '/assets/styles.css'
    # })

    return layout