# app/layout.py
import pandas as pd
import dash_leaflet as dl
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import yaml
import os
from dash import html, dcc, _dash_renderer
from datetime import date, datetime
from babel.dates import format_datetime
from arcgis.gis import GIS
from arcgis.mapping import WebMap
from arcgis.features import FeatureLayer
from utils.request_gp.utils import descifrar_datos

_dash_renderer._set_react_version("18.2.0")

## Se configuran usuarios y contraseñas de portal de ArcGIS
# 1. Cargar configuración desde config.yml
base_dir = os.path.dirname(os.path.abspath(__file__))  # Obtiene el directorio de layout.py
config_path = os.path.join(base_dir, "../utils/request_gp/config.yaml")

with open(config_path, "r") as file:
    config = yaml.safe_load(file)

# 2. Obtener datos cifrados desde el archivo
url = config["portal"]["url"]
usuario_cifrado = config["portal"]["usuario"]
password_cifrado = config["portal"]["password"]
fernet_key = config["portal"]["fernet_key"]

# 3. Descifrar usuario y contraseña
usuario, password = descifrar_datos(usuario_cifrado, password_cifrado, fernet_key)

# 4. Instanciar GIS con los datos descifrados
if usuario and password:
    gis = GIS(url, usuario, password)
    print("Conexión establecida correctamente.")
else:
    print("Error: No se pudo descifrar el usuario o la contraseña.")

# Configurar la fecha en español
#fecha_actual = datetime.now().date()
#fecha_espanol = format_datetime(fecha_actual, "EEEE, d 'de' MMMM 'de' yyyy", locale='es')

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
    layout = dmc.MantineProvider(
        children=[
            html.Div([
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
                        html.H1("Certificaciones del estado del tiempo y clima - IDEAM", 
                                style={'font-family': 'arial', 'text-align': 'center'}, #, 'font-weight': 'bold'
                                title="Datos obtenidos de la red de observación en superficie IDEAM "),
                        # Espaciador
                        html.Div(style={'height': '10px', 'width': '100%'}),
                        html.P("Instrucciones:", style={'font-family': 'arial', 'text-align': 'justify','font-size': 15,
                                                        'font-weight': 'bold', 'margin-bottom': '5px'}),
                        html.P("Respetado usuario, en esta aplicación podrá obtener certificaciones del estado del tiempo;\
                                para ello se solicitarán sus datos personales, de contacto, variable meteorológica, periodo,\
                                ubicación y fechas de interés. Recuerde que puede disponer de un shape completo (archivos .cpg,\
                                .dbf, .prj, .sbn, .sbx, .shp, .shx) y comprimido en .zip para ubicar el punto de interés o\
                                hacer click en el mapa más adelante.",
                                style={'font-family': 'arial', 'text-align': 'justify', 'margin-bottom': '20px',
                                    'font-size': 15}),
                        html.P(["En esta aplicación, se generará una certificación por variable y periodo, si requiere más, recargue la página luego de terminar el proceso.\
                                El diligenciamiento de todos los campos ES OBLIGATORIO para obtener el documento. Tenga\
                            en cuenta la ",
                            dcc.Link("política de tratamiento y protección de datos personales.",
                                        href="https://www.ideam.gov.co/sites/default/files/archivos/politica_de_tratamiento_y_proteccion_de_datos_personales_0.pdf",
                                        target="_blank")],
                            style={'text-align': 'justify', 'margin-bottom': '20px', 'font-weight': 'bold', 'font-size': 15}), #'font-family': 'arial', 
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
                                            'Permiso de protección temporal - PPT'], id="tdoc-dp"), #value='Cédula de ciudadanía', 
                            ], style={'flex': '1', 'padding': '0 6px', 'font-size': 12}),                                               
                            html.Div([
                                html.Label("Número de documento:", style={
                                    'font-family': 'arial', 'color': '#5D5D5D', 'font-size': 13, 'width': '100%'}),
                                dcc.Input(id="ndoc-input", type="number", placeholder='Digite su n.° de documento', maxLength=10,
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
                                dcc.Dropdown(['Femenino', 'Masculino', 'No deseo registrar esta información', 'Otro'], #value='Femenino', 
                                            id="genero-dp"),
                                html.Label("¿Cuál?", style={
                                    'font-family': 'arial', 'color': '#5D5D5D', 'font-size': 13}),
                                dcc.Input(id="genero-input", type="text", placeholder='Digite el género'),
                            ], style={'flex': '1', 'padding': '0 6px', 'width': '180px', 'font-size': 12}),
                            html.Div([
                                html.Label("Grupo étnico:", style={
                                        'font-family': 'arial', 'color': '#5D5D5D', 'font-size': 13}),
                                dcc.Dropdown(['Indígena', 'Gitano (rom)', 'Negro, mulato, afrodescendiente, afrocolombiano, raizal o Palenquero',
                                        'Otro','Ninguno'], id="grupetn-dp"), # value='Indígena',
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
                                            'Ninguno'], id="infpoblac-dp"), #value='Niños, Niñas y Adolescentes',
                            ], style={'flex': 1, 'padding': '0 10px', 'min-width': '80px', 'font-size': 12}),

                            html.Div([
                                html.Label("¿Presenta discapacidad?", style={
                                        'font-family': 'arial', 'color': '#5D5D5D', 'font-size': 13}),
                                dcc.Dropdown(['Física', 'Auditiva', 'Visual','Sordoceguera', 'Intelectual – Cognitiva',
                                            'Psicosocial', 'Talla baja','Otra','Ninguna'], id="discap-dp"), #value='Física'
                                html.Label("¿Cuál?", style={
                                        'font-family': 'arial', 'color': '#5D5D5D', 'font-size': 13}),
                                dcc.Input(id="discap-input", type="text", placeholder='Digite la discapacidad'),
                            ], style={'flex': 1, 'padding': '0 10px', 'min-width': '80px', 'font-size': 12}),

                            html.Div([
                                html.Label("Grupo de interés:", style={
                                        'font-family': 'arial', 'color': '#5D5D5D', 'font-size': 13}),
                                dcc.Dropdown(['Ciudadano', 'Empresa privada', 'Academia','Ente de control', 'Medio de comunicación',
                                            'Extranjero', 'Entidad pública','Organismo internacional', 'Usuario interno o colaborador',
                                            'Otro'], id="ginteres-dp"), # value='Ciudadano',
                                html.Label("¿Cuál?", style={
                                        'font-family': 'arial', 'color': '#5D5D5D', 'font-size': 13}),
                                dcc.Input(id="ginteres-input", type="text", placeholder='Digite el grupo de interés'),
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
                                dcc.Input(id="correo-input", type="email", placeholder='Digite su correo electrónico',
                                        style={'width': '100%'}),
                            ], style={'flex': 1, 'padding': '0 10px', 'min-width': '70px'}),

                            html.Div([
                                html.Label("Teléfono de contacto:", style={
                                        'font-family': 'arial', 'color': '#5D5D5D', 'font-size': 13}),
                                dcc.Input(id="tel-input", type="number", placeholder='Digite su número de contacto',style={'width': '100%'}),
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

                        html.Div([
                                html.P("Por favor, seleccione la fecha inicial y la fecha final de interés para su certificación.",
                                    style={'font-family': 'arial', 'text-align': 'justify'}),#, 'margin-bottom': '20px'}),
                            ], style={'height': '20px', 'width': '100%'}),

                        # Espaciador
                        html.Div(style={'height': '15px', 'width': '100%'}),

                        html.Div([
                            html.Div([
                                html.Label("Fecha inicial:", style={'font-family': 'arial', 'text-align': 'center',
                                                                'font-weight': 'bold', 'font-size': 13}),
                                dmc.DatePickerInput(
                                    id="inidate-pckr",
                                    description="Escoja la fecha inicial de su periodo de interés",
                                    minDate=date(1940, 1, 1),
                                    maxDate=datetime.now().date(),
                                    clearable=True,
                                    placeholder='DD/MM/YYYY',
                                    #value=date(2020, 12, 31),
                                    valueFormat="DD/MM/YYYY",  # or string in the format "YYYY-MM-DD"
                                    w=250,
                                ),
                                dmc.Space(h=10),
                            ], style={'flex':1, 'padding':'0 10px', 'min-width': '200px',
                                    'max-width': '50%','box-sizing': 'border-box'}),#'display': 'flex', 'justify-content': 'space-between', 'flex-wrap': 'wrap'}),
                            
                            html.Div([
                                html.Label("Fecha final:", style={'font-family': 'arial', 'text-align': 'center',
                                                                'font-weight': 'bold', 'font-size': 13}),

                                dmc.DatePickerInput(
                                    id="findate-pckr",
                                    description="Escoja la fecha final de su periodo de interés",
                                    minDate=date(1940, 8, 5),
                                    maxDate=datetime.now().date(),
                                    placeholder='DD/MM/YYYY',
                                    #value=datetime.now().date(),
                                    clearable=True,
                                    valueFormat="DD/MM/YYYY",  # or string in the format "YYYY-MM-DD"
                                    w=250,
                                ),
                                dmc.Space(h=10),
                            ], style={'flex':1, 'padding':'0 10px', 'min-width': '200px',
                                    'max-width': '50%','box-sizing': 'border-box'}),
                            
                            # html.Div([
                            #     # Espacio en blanco
                            # ], style={'flex': 1, 'padding': '0 10px', 'min-width': '70px',
                            #           'max-width': '20%','box-sizing': 'border-box'}),
                        ], style={'display': 'flex', 'justify-content': 'space-between', 'flex-wrap': 'wrap',
                                'gap': '10px','width': '100%'} ),
                        
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
                            html.Div(id='upload-status'),
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
                            dcc.Store(id='file-storage', storage_type='session'), 
                        ]),

                        # Espaciador
                        html.Div(style={'height': '20px', 'width': '100%'}),
                        
                        html.P("Coordenadas de su punto de interés:",
                            style={'font-family': 'arial', 'text-align': 'justify', 'margin-bottom': '2px'}),
                        html.Div(id="click-info"),  # Div para mostrar la información del clic

                        # Espaciador
                        html.Div(style={'height': '20px', 'width': '100%'}),

                        html.P("Puede guiarse de las estaciones meteorológicas cercanas con este listado y luego hacer click:",
                            style={'font-family': 'arial', 'text-align': 'justify', 'margin-bottom': '2px'}),

                        dcc.Dropdown(
                            id='estacion-dropdown',
                            options=[{'label': nombre, 'value': nombre} for nombre in sorted(data['nombre'])],
                            style={'font-family': 'arial'},
                            value=sorted(data['nombre'])[0]  # Valor por defecto
                        ),
                        
                        html.Div([
                            dl.Map(center=[4, -74], zoom=7, 
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
                                style={'width': '100%', 'height': '90vh'}, id="map"),
                        ]),

                        # Espaciador
                        html.Div(style={'height': '20px', 'width': '100%'}),

                        html.P("Haga click en el botón 'Analizar estaciones representativas' para ejecutar el análisis\
                                de representatividad de estaciones meteorológicas. Una vez se encuentre la estación más\
                                representativa, el sistema generará su certificación.",
                            style={'font-family': 'arial', 'text-align': 'justify', 'margin-bottom': '10px'}),

                        html.P("Una vez termine de generarse su documento, se habilitará el botón 'Descargar certificación'.",
                            style={'font-family': 'arial', 'text-align': 'justify', 'margin-bottom': '20px', 'font-weight': 'bold',
                                'font-size': 16}),

                        dcc.Store(id='gp-result-store'),
                        html.Div(id="output-represanalis"),

                        dcc.Store(id='certtyc-result-store'),
                        #html.Div(id='output-state'),

                        # Mostrar indicador de carga
                        dcc.Loading(
                            id="loading-indicator",
                            type="circle",  # Tipo de loading (circle, dot, o default)
                            children=html.Div(id="output-state"),  # Div de salida
                            fullscreen=True,
                            overlay_style={"visibility":"visible", "filter": "blur(2px)"},
                            #overlay_style={"visibility":"visible", "opacity": .5, "backgroundColor": "white"},
                            custom_spinner=html.H2(["Espere unos minutos mientras se genera su certificación", dbc.Spinner(color="#0090FF")],
                                                style={'text-align': 'center'})
                            ),
                        
                        dcc.Store(id="message-store"),

                        html.Div([
                            html.Button("Analizar estaciones representativas", style={
                                    'font-family': 'arial'}, id="represanalis-button"),
                            html.Button("Descargar certificación", id="descargar-button", disabled=True),
                            dcc.Download(id="download-certif")
                        ]),

                        dcc.Store(id="pdf_data"),
                        
                        # Espaciador
                        html.Div(style={'height': '20px', 'width': '100%'}),
                        
                        dcc.ConfirmDialog(
                            id='esperar-dialog',
                            message='Se habilitó el botón de "Descargar certificación".',
                            ),

                        dcc.ConfirmDialog(
                            id='esperarpdf-dialog',
                            message='Por favor, espere mientras se descarga su certificación. No refresque la página',
                            ),
                            
                        # Espaciador
                        html.Div(style={'height': '20px', 'width': '100%'}),

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

                ], style={'width': '100%', 'max-width': '1200px', 'margin': '0 auto'}),
        ]),

    return layout