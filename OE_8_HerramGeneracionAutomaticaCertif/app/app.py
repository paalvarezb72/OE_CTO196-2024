# app/app.py
import dash
from app.layout import create_layout
from app.callbacks import register_callbacks

external_stylesheets = ['https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css',
                        '/assets/styles.css'
                            ]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "Certificaciones estado tiempo y clima"
#server = app.server
#server.config['REQUEST_TIMEOUT'] = 360

def initialize_app(data):
    app.layout = create_layout(app, data)
    register_callbacks(app,data)
    return app
