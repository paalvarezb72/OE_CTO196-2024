import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State
import pandas as pd
import plotly.express as px
import geopy.distance 
#from dash.exceptions import PreventUpdate

## Lectura de CNE de convencionales activas
EstCON_Act = pd.read_excel('EstacCON_IDEAM_Activas.xls')

app = dash.Dash(__name__)

app.layout = html.Div([
    dcc.Graph(
        id='mapa-estaciones',
        figure=px.scatter_mapbox(EstCON_Act,
                                 lat="latitud",
                                 lon="longitud",
                                 hover_name="nombre",
                                 zoom=10,
                                 mapbox_style="open-street-map"),
        style={'height': '50vh'},
        config={'staticPlot': False, 'scrollZoom': True, 'doubleClick': 'reset'}
    ),
    html.Div([
        html.P("Latitud del punto de interés:"),
        dcc.Input(id="lat-input", type="number", placeholder="Ingrese la latitud", debounce=True),
        html.P("Longitud del punto de interés:"),
        dcc.Input(id="lon-input", type="number", placeholder="Ingrese la longitud", debounce=True),
        html.Button("Calcular Distancia", id="calculate-distance-btn"),
    ]),
    html.Div(id="distance-info"),
    html.Button('Reiniciar selección', id='reset-button', n_clicks=0),
])

@app.callback(
    Output('distance-info', 'children'),
    Input('calculate-distance-btn', 'n_clicks'),
    State('mapa-estaciones', 'clickData'),
    State('lat-input', 'value'),
    State('lon-input', 'value')
)
def calculate_distance(n_clicks, clickData, lat, lon):
    if n_clicks is None or clickData is None:
        return "Seleccione una estación, luego, cuando vea el marcador rojo, introduzca las coordenadas \
            de su punto de interés y oprima el botón 'Calcular distancia'."

    estacion_lat = clickData['points'][0]['lat']
    estacion_lon = clickData['points'][0]['lon']

    if lat is None or lon is None:
        return "Por favor, introduzca las coordenadas del punto de interés."

    distancia = geopy.distance.distance((estacion_lat, estacion_lon), (lat, lon)).km
    return f"La distancia es: {distancia:.2f} km."

@app.callback(
    [Output('mapa-estaciones', 'figure'),
     Output('lat-input', 'value'),
     Output('lon-input', 'value')],
    [Input('reset-button', 'n_clicks'),
     Input('mapa-estaciones', 'clickData')],
    prevent_initial_call=True
)
def update_map(n_clicks, clickData):
    ctx = dash.callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if triggered_id == 'reset-button':
        fig = px.scatter_mapbox(EstCON_Act,
                                lat="latitud",
                                lon="longitud",
                                hover_name="nombre",
                                zoom=10,
                                mapbox_style="open-street-map")
        return fig, None, None  # Reset everything

    if clickData:
        lat = clickData['points'][0]['lat']
        lon = clickData['points'][0]['lon']
        fig = px.scatter_mapbox(EstCON_Act,
                                lat="latitud",
                                lon="longitud",
                                hover_name="nombre",
                                zoom=10,
                                mapbox_style="open-street-map")
        fig.add_scattermapbox(lat=[lat], lon=[lon], marker={'size': 14, 'color': 'red'})
        return fig, None, None  # Update map with the station marker

    return dash.no_update

if __name__ == '__main__':
    app.run_server(debug=True)
