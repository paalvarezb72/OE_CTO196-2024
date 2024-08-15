# app/layout.py
from dash import html, dcc
import plotly.express as px
import pandas as pd
import dash_leaflet as dl
from arcgis.gis import GIS
from arcgis.mapping import WebMap
from arcgis.features import FeatureLayer
#from data.data_reading import data_locLims
#from app.app import app

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
    # Se crean marcadores a partir de los datos
    markers = [
        dl.Marker(position=[row['latitud'], row['longitud']], 
                  children=[
                      dl.Tooltip(row['nombre']),
                      dl.Popup(f"Altitud: {row['altitud']}")
                  ],
                  id={"type": "marker", "index": i})  # Añadir un identificador único para cada marcador
        for i, row in data.iterrows()
    ]
    # fig = px.scatter_mapbox(data,
    #                         lat="latitud",
    #                         lon="longitud",
    #                         hover_name="nombre",
    #                         hover_data={"altitud": True},
    #                         zoom=10,
    #                         mapbox_style="open-street-map")
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
            html.Img(src=app.get_asset_url('LOGO_AMBIENTE_2024_2.png'), style={
                    'display': 'inline-block', 'width': '10%'}),
        ], style={'margin-left': '5%', 'margin-right': '5%','width': '100%', 'display': 'flex',
                  'justify-content': 'space-between', 'align-items': 'center'}),

        html.Div(style={'height': '10px', 'width': '100%'}),

        # Contenedor del resto de contenidos
        html.Div(
            # Ajusta los márgenes según necesites
            style={'margin-left': '5%', 'margin-right': '5%'},
            children=[
                html.H1("Certificaciones del estado del tiempo y del clima - IDEAM", style={'font-family': 'arial', 'text-align': 'center'},
                        title="Datos obtenidos de la red IDEAM "),

                html.P("Respetado usuario, diligiencie todos los campos para obtener su certificación:",
                    style={'font-family': 'arial', 'text-align': 'justify', 'margin-bottom': '20px'}),

                html.Div([
                    html.Div([
                        html.Label("Tipo solicitante:", style={
                                'font-family': 'arial', 'color': '#5D5D5D', 'font-size': 15}),
                        dcc.RadioItems(['Persona natural', 'Persona jurídica'], value='Persona natural', id="tpersona-ri"),
                    ], style={'flex': 1, 'padding': '0 10px', 'min-width': '60px', 'font-size': 12}),

                    html.Div([
                        html.Label("Tipo identificación:", style={
                                'font-family': 'arial', 'color': '#5D5D5D', 'font-size': 15}),
                        dcc.Dropdown(['Cédula de ciudadanía', 'Tarjeta de identidad', 'Cédula de extranjería',
                                  'Pasaporte', 'Permiso especial de permanencia - PEP',
                                   'Permiso de protección temporal - PPT'], value='Cédula de ciudadanía', id="tdoc-ri"),
                    ], style={'flex': 1, 'padding': '0 10px', 'min-width': '100px', 'font-size': 12}),
                                       
                    html.Div([
                        html.Label("Número identificación:", style={
                                'font-family': 'arial', 'color': '#5D5D5D', 'font-size': 15}),
                        dcc.Input(id="cc-input", type="number", placeholder='1234567890'),
                    ], style={'flex': 1, 'padding': '0 10px', 'min-width': '70px'}),
                                                       
                    html.Div([
                        html.Label("Nombre(s):", style={
                                'font-family': 'arial', 'color': '#5D5D5D', 'font-size': 15}),
                        dcc.Input(id="nombres-input", type="text", placeholder='Nombres'),
                    ], style={'flex': 1, 'padding': '0 10px', 'min-width': '150px'}),

                    html.Div([
                        html.Label("Apellido(s):", style={
                                'font-family': 'arial', 'color': '#5D5D5D', 'font-size': 15}),
                        dcc.Input(id="apellidos-input", type="text", placeholder='Apellidos'),
                    ], style={'flex': 1, 'padding': '0 10px', 'min-width': '150px'}),
                ], style={'display': 'flex', 'justify-content': 'space-between', 'flex-wrap': 'wrap'}),

                # Espaciador
                html.Div(style={'height': '10px', 'width': '100%'}),
                # Contenedor resto de información personal
                html.Div([
                    html.Div([
                        html.Label("Correo:", style={
                                'font-family': 'arial', 'color': '#5D5D5D', 'font-size': 15}),
                        dcc.Input(id="correo-input", type="email", placeholder='Correo electrónico'),
                    ], style={'flex': 1, 'padding': '0 10px', 'min-width': '150px'}),

                    html.Div([
                        html.Label("Teléfono de contacto:", style={
                                'font-family': 'arial', 'color': '#5D5D5D', 'font-size': 15}),
                        dcc.Input(id="tel-input", type="number", placeholder='3124567890'),
                    ], style={'flex': 1, 'padding': '0 10px', 'min-width': '70px'}),

                    html.Div([
                        html.Label("Género:", style={
                                'font-family': 'arial', 'color': '#5D5D5D', 'font-size': 15}),
                        dcc.Dropdown(['Femenino', 'Masculino', 'No deseo registrar esta información',
                                  'No aplica'], value='Femenino', id="genero-dp"),
                    ], style={'flex': 1, 'padding': '0 10px', 'min-width': '80px', 'font-size': 12}),
                    
                    html.Div([
                        html.Label("Otro género, ¿cuál?", style={
                                'font-family': 'arial', 'color': '#5D5D5D', 'font-size': 15}),
                        dcc.Input(id="genero-input", type="text", placeholder='Digite el género'),
                    ], style={'flex': 1, 'padding': '0 10px', 'min-width': '100px', 'font-size': 12}),

                ], style={'display': 'flex', 'justify-content': 'space-between', 'flex-wrap': 'wrap'}),
                
                # Espaciador
                html.Div(style={'height': '10px', 'width': '100%'}),
                # Contenedor resto de información personal
                html.Div([
                    html.Div([
                        html.Label("Grupo étnico:", style={
                                'font-family': 'arial', 'color': '#5D5D5D', 'font-size': 15}),
                        dcc.Dropdown(['Indígena', 'Gitano (rom)', 'Negro, mulato, afrodescendiente, afrocolombiano, raizal o Palenquero',
                                  'No aplica'], value='Femenino', id="grupetn-dp"),
                        html.Label("Otro, ¿cuál?", style={
                                'font-family': 'arial', 'color': '#5D5D5D', 'font-size': 15}),
                        dcc.Input(id="grupetn-input", type="text", placeholder='Digite el grupo étnico'),
                    ], style={'flex': 1, 'padding': '0 10px', 'min-width': '80px', 'font-size': 12}),
                    
                    html.Div([
                        html.Label("Información poblacional:", style={
                                'font-family': 'arial', 'color': '#5D5D5D', 'font-size': 15}),
                        dcc.Dropdown(['Niños, Niñas y Adolescentes', 'Adulto Mayor', 'Mujer cabeza de familia',
                                      'Personas en condición de discapacidad', 'Población LGBTIQ+',
                                      'Personas desplazadas por la violencia y aquellas que se encuentran en pobreza extrema',
                                      'No aplica'], value='Niños, Niñas y Adolescentes', id="infpoblac-dp"),
                    ], style={'flex': 1, 'padding': '0 10px', 'min-width': '80px', 'font-size': 12}),

                    html.Div([
                        html.Label("¿Presenta discapacidad?", style={
                                'font-family': 'arial', 'color': '#5D5D5D', 'font-size': 15}),
                        dcc.Dropdown(['Física', 'Auditiva', 'Visual','Sordoceguera', 'Intelectual – Cognitiva',
                                      'Psicosocial', 'Talla baja','No aplica'], value='Física', id="discapacidad-dp"),
                        html.Label("Otro, ¿cuál?", style={
                                'font-family': 'arial', 'color': '#5D5D5D', 'font-size': 15}),
                        dcc.Input(id="discapacidad-input", type="text", placeholder='Digite el grupo étnico'),
                    ], style={'flex': 1, 'padding': '0 10px', 'min-width': '80px', 'font-size': 12}),

                    html.Div([
                        html.Label("Grupo de interés:", style={
                                'font-family': 'arial', 'color': '#5D5D5D', 'font-size': 15}),
                        dcc.Dropdown(['Ciudadano', 'Empresa privada', 'Academia','Ente de control', 'Medio de comunicación',
                                      'Extranjero', 'Entidad pública','Organismo internacional', 'Usuario interno o colaborador'], value='Física', id="ginteres-dp"),
                        html.Label("Otro, ¿cuál?", style={
                                'font-family': 'arial', 'color': '#5D5D5D', 'font-size': 15}),
                        dcc.Input(id="ginteres-input", type="text", placeholder='Digite el grupo étnico'),
                    ], style={'flex': 1, 'padding': '0 10px', 'min-width': '80px', 'font-size': 12}),                   
                ], style={'display': 'flex', 'justify-content': 'space-between', 'flex-wrap': 'wrap'}),

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
                                'font-family': 'arial', 'color': '#5D5D5D', 'font-size': 15}),
                        dcc.Dropdown(
                            id="variable-dropdown",
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
                                'font-family': 'arial', 'color': '#5D5D5D', 'font-size': 15}),
                        dcc.Dropdown(id="tiposerie-dropdown",
                                    style={'font-family': 'arial'})
                    ], style={'flex': 1, 'padding': '0 10px', 'min-width': '300px'}),

                ], style={'display': 'flex', 'justify-content': 'space-between', 'flex-wrap': 'wrap'}),

                # Espaciador
                html.Div(style={'height': '20px', 'width': '100%'}),

                html.P("Por favor, escoja las fechas de interés para su certificación. Si  requiere\
                    un rango, seleccione solo los días/meses/años correspondientes a la fecha inicial y final:",
                    style={'font-family': 'arial', 'text-align': 'justify', 'margin-bottom': '20px'}),

                html.Div([
                    html.Div([
                        html.Label("Día(s):", style={
                                'font-family': 'arial', 'color': '#5D5D5D', 'font-size': 15}),
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
                                'font-family': 'arial', 'color': '#5D5D5D', 'font-size': 15}),
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
                                'font-family': 'arial', 'color': '#5D5D5D', 'font-size': 15}),
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

                html.P("En el siguiente mapa, busque por favor su área de interés, \
                    desplácese en este manteniendo oprimido el clic izquierdo del cursor \
                    y observe el nombre de la estación meteorológica más cercana, tenga en \
                    cuenta el nombre obtenido.",
                    style={'font-family': 'arial', 'text-align': 'justify', 'margin-bottom': '20px'}),

                html.P("Recuerde que una estación se considera cercana si se encuentra a una distancia\
                    inferior a 10 km planos del punto de interés -si la variable de interés es velocidad\
                        del viento, la distancia debe ser inferior a 3 km-, no obstante, considere que aún\
                        dentro de ese radio, una diferencia elevada de altitudes de la estación con respecto\
                        a su punto de interés, es decir, superior a los 200msnm, (entre otros factores) \
                        puede significar que esta no sea representativa para su zona de estudio. \
                        A continuación, puede calcular las distancias lineales siguiendo las instrucciones.",
                    style={'font-family': 'arial', 'text-align': 'justify', 'margin-bottom': '20px', 'font-style': 'italic'}),

                html.Div([

                    html.P("Calcule la distancia de la estación cercana a su punto de interés",
                        style={'font-size': 16, 'font-family': 'arial', 'margin-top': '20px', 'font-weight': 'bold'}),
                    html.Div(id="distance-info",
                            style={'height': '20px', 'width': '100%'}),

                    # Espaciador
                    html.Div(style={'height': '20px', 'width': '100%'}),

                    html.Div([
                        html.Label("Latitud del punto de interés:", style={
                                'font-family': 'arial', 'color': '#5D5D5D', 'font-size': 15}),
                        dcc.Input(id="lat-input", type="number",
                                placeholder="P. e.: -2.64"),
                    ], style={'flex': 1, 'padding': '0 10px', 'min-width': '200px'}),

                    html.Div([
                        html.Label("Longitud del punto de interés:", style={
                                'font-family': 'arial', 'color': '#5D5D5D', 'font-size': 15}),
                        dcc.Input(id="lon-input", type="number",
                                placeholder="P. e.: -74.86"),
                    ], style={'flex': 1, 'padding': '0 10px', 'min-width': '200px'}),

                    html.Button("Calcular distancia", id="calculate-distance-btn",
                                style={'font-family': 'arial', 'flex': 1, 'padding': '0 10px', 'min-width': '150px'}),
                    html.Button('Reiniciar selección', id='reset-button', n_clicks=0,
                                style={'font-family': 'arial', 'flex': 1, 'padding': '0 10px', 'min-width': '150px'}),
                ], style={'display': 'flex', 'justify-content': 'space-between', 'flex-wrap': 'wrap'}),

                # dcc.Graph(id="mapa-estaciones",
                #         figure=fig,
                #         config={"scrollZoom": True, "responsive": True},
                #         style={"height": "500px", 'font-family': 'arial'},
                # ),

                html.Div([
                    html.Div(id="click-info"),  # Div para mostrar la información del clic
                    dl.Map(center=[4, -74], zoom=10, 
                        children=[
                            dl.TileLayer(),  # Capa base
                            dl.LayerGroup(markers),  # Capas de marcadores
                            dl.LayerGroup(id="click-layer")  # Capa para los clics
                        ], 
                        style={'width': '100%', 'height': '50vh'}, id="map"),
                ]),

                html.Div(id="click-info"),  # Div para mostrar la información del clic

                html.Div([
                    dcc.Upload(
                        id='upload-zip',
                        children=html.Div([
                            'Arrastra y suelta o ',
                            html.A('Selecciona un archivo .zip')
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
                    html.Div(id='upload-status')
                ]),
                
                html.Div([
                    html.P("Si ninguna estación es cercana o de similar altitud a su punto de interés,\
                        por favor seleccione el siguiente ítem (recuerde antes haber registrado\
                        las coordenadas de este con la anterior herramienta)",
                        style={'font-family': 'arial', 'font-size': 13}),#, 'margin-top': '20px', }),
                    
                    dcc.RadioItems(
                        options=[{'label': 'Sin estaciones representativas', 'value': 'no_station'}],
                        value=None,
                        id='sin-estaciones',
                        style={'font-family': 'arial', 'font-size': 13}
                    ),
                    html.Div(id='hidden-div', style={'display': 'none'})
                    
                ], style={'display': 'flex', 'justify-content':'space-between'}),#, 'flex-wrap': 'wrap'}),

                html.P("A partir del ejercicio anterior, seleccione la estación de su interés",
                    style={'font-family': 'arial', 'margin-top': '20px'}),

                dcc.Dropdown(
                    id='estacion-dropdown',
                    options=[{'label': nombre, 'value': nombre}
                            for nombre in data['nombre']],
                    style={'font-family': 'arial'},
                    value=data['nombre'][0]  # Valor por defecto
                ),

                # Espaciador
                html.Div(style={'height': '20px', 'width': '100%'}),

                html.Div(id='output-state'),

                html.Div(style={'height': '10px', 'width': '100%'}),

                html.Button("Generar Certificación", style={
                            'font-family': 'arial'}, id="generar-button"),

                html.Div(style={'height': '10px', 'width': '100%'}),

                html.P([
                    "Al generar su certificación, usted acepta la política tratamiento y protección de datos personales, la cual, puede consultar en ",
                    dcc.Link("este enlace", href="https://www.ideam.gov.co/sites/default/files/archivos/politica_de_tratamiento_y_proteccion_de_datos_personales.pdf", 
                             target="_blank"),"."
                ], style={'font-family': 'arial', 'text-align': 'justify', 'margin-bottom': '20px'}),

                html.P(["Si requiere una certificación con información adicional -fenómenos, anomalías,\
                        análisis climatológicos, entre otros-, por favor tramite su solicitud al correo electrónico ",
                        html.A("contacto@ideam.gov.co", href="mailto:contacto@ideam.gov.co")," o a través del siguiente enlace: ",
                        dcc.Link("Formulario web", href="http://sgdorfeo.ideam.gov.co/orfeo6.1/formularioWeb/", target="_blank"),"."
                ], style={'font-family': 'arial', 'text-align': 'justify', 'margin-bottom': '20px'}),

                # Espaciador
                html.Div(style={'height': '20px', 'width': '100%'})

            ]),

        html.Footer([
            html.Div([
                html.Div([
                    html.H3("Instituto de Hidrología, Meteorología y Estudios Ambientales"),
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
                        html.A(html.Img(src="/assets/facebook-icon.png", alt="Facebook"), href="https://www.facebook.com/IDEAM.INSTITUTO"),
                        html.A(html.Img(src="/assets/twitter-icon.png", alt="Twitter"), href="https://twitter.com/IDEAMCOLOMBIA"),
                        html.A(html.Img(src="/assets/instagram-icon.png", alt="Instagram"), href="https://www.instagram.com/IDEAMCOLOMBIA"),
                        html.A(html.Img(src="/assets/youtube-icon.png", alt="YouTube"), href="https://www.youtube.com/user/INSTITUTOIDEAM")
                    ], style={'display': 'flex', 'gap': '10px', 'margin-top': '10px'})
                ], className='footer-left'),
                html.Div([
                    html.Img(src="/assets/logo-ambiente.png", alt="Ambiente", style={'max-height': '100px'})
                ], className='footer-right')
            ], className='footer-container'),
            html.Div([
                html.A("Políticas", href="#"),
                html.A("Mapa del sitio", href="#"),
                html.A("Términos y condiciones", href="#"),
                html.A("Accesibilidad", href="#")
            ], className='footer-bottom')
        ], className='footer')
    
        ], style={'width': '100%', 'max-width': '1200px', 'margin': '0 auto'})
    
    # app.css.append_css({
    #     'external_url': 'https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css'
    # })

    # app.css.append_css({
    #     'external_url': '/assets/styles.css'
    # })

    return layout

# Se llama la función data_locLims para obtener los datos
#data = data_locLims()
#layout = create_layout(data)