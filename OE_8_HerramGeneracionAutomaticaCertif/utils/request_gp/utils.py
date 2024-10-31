import logging
import os
import yaml
from cryptography.fernet import Fernet


current_dir = os.path.dirname(os.path.abspath(__file__))

log_file_path = os.path.join(current_dir, 'certificado_tyc_request_gp.log')

logging.basicConfig(
    filename=log_file_path,
    level=logging.INFO,
    format='%(asctime)s %(levelname)s:%(message)s',
    encoding='utf-8'
)
def addMessage(message):
    '''Agrega el mensaje enviado a la traza.
    Par\xe1metros:
    - message: Cadena de texto con informaci\xf3n relevante
             al funcionamiento del servicio
    '''
    logging.info(message)
    return print("{}".format(message))

def obtener_configuracion():
    """
    Obtiene todo el contenido del archivo de configuración YAML.

    Returns:
        dict: El contenido del archivo de configuración YAML.

    """
    directorio_actual = os.path.dirname(os.path.realpath(__file__))
    archivo_yaml = os.path.join(directorio_actual, "config.yaml")
    
    with open(archivo_yaml, 'r', encoding='utf-8') as file:
        data = yaml.safe_load(file)
    
    return data

def descifrar_datos(usuario_cifrado, password_cifrado, clave_fernet_str):
    """
    Función para descifrar el usuario y la contraseña.
    Asume que clave_fernet_str es una cadena base64 válida.
    """
    addMessage("Iniciando el proceso de descifrado...")
    
    try:
        addMessage("Descifrando los datos...")
        clave_fernet_str_encode = clave_fernet_str.encode()
        fernet = Fernet(clave_fernet_str_encode)
        
        # Descifrar los datos
        usuario_descifrado = fernet.decrypt(usuario_cifrado.encode()).decode()
        password_descifrado = fernet.decrypt(password_cifrado.encode()).decode()
        
        addMessage("Descifrado completado exitosamente.")
        
        return usuario_descifrado, password_descifrado
    except Exception as e:
        addMessage(f"Error durante el descifrado: {e}")
        return None, None
    
