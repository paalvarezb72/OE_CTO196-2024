import dash
from dash import html
import dash_leaflet as dl
from dash.dependencies import Input, Output
from arcgis.gis import GIS
from arcgis.mapping import WebMap
from arcgis.features import FeatureLayer

# Inicializa la aplicación Dash
app = dash.Dash(__name__)

# Conéctate a ArcGIS Online
gis = GIS("https://visualizador.ideam.gov.co/portal", "GDRM_IDEAM", "Meteo2024.")

# Obtén el WebMap de ArcGIS Online
webmap_item = gis.content.get("8ac9fc5932e74b07b2c5b0d6be3eec8e")
webmap = WebMap(webmap_item)

# Extrae las capas del WebMap
layers = []

"""
for layer in webmap.layers:
    geojson = FeatureLayer(layer.url).query(where="1=1", out_sr=4326, return_geometry=True).to_geojson
    layers.append(dl.TileLayer(url=geojson))

"""
for layer in webmap.layers:
    layers.append(dl.TileLayer(url=layer.url))
    print(layer.url)

# Define el layout de la aplicación
app.layout = html.Div([
    dl.Map(center=[4, -74], zoom=10, 
        children=[
            dl.TileLayer(),  # Capa base
            *layers,  # Capas del WebMap
            dl.LayerGroup(id="click-layer")  # Capa para los clics
        ], 
        style={'width': '100%', 'height': '50vh'}, id="map"),
    html.Div(id="click-info")  # Div para mostrar la información del clic
])

# Define el callback para el evento de clic
@app.callback(
    Output("click-info", "children"),
    Input("map", "clickData")
)
def display_click_info(click_lat_lng):
    if click_lat_lng is None:
        return "Haz clic en el mapa para obtener las coordenadas."
    
    print(click_lat_lng)
    
    lat, lng = click_lat_lng["latlng"]["lat"], click_lat_lng["latlng"]["lng"]
    return f"Coordenadas del clic: Latitud {lat}, Longitud {lng}"

# Ejecuta la aplicación
if __name__ == '__main__':
    app.run_server(debug=True)