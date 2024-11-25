# run.py
from utils.db_connection import create_connection
from data.data_reading import data_locLims
from app.app import initialize_app

if __name__ == '__main__':
    # Establecer la conexión a la base de datos (si es necesario)
    conn = create_connection()
    
    # Obtener los datos necesarios
    data = data_locLims()
    
    # Inicializar la aplicación con los datos
    app = initialize_app(data)
    
    # Ejecutar el servidor
    #app.run_server(debug=True)
    app.run_server(host="192.168.154.16", port=8050, debug=True)