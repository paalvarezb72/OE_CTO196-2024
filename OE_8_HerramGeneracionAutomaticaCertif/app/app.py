# app/app.py
import dash
from app.layout import create_layout
from app.callbacks import register_callbacks

app = dash.Dash(__name__)
app.title = "Certificaciones estado tiempo y clima"

def initialize_app(data):
    app.layout = create_layout(app, data)
    register_callbacks(app,data)
    return app
