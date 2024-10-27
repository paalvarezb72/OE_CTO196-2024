# docs/convert_topdf.py
import pythoncom
import time
import io
import os
from docx2pdf import convert

def convertir_a_pdf(nombre_archivo_final):
    # Espera un segundo para asegurarse de que el archivo .docx esté completamente guardado
    time.sleep(1)
    if os.path.exists(nombre_archivo_final):
        try:
            # Inicializar COM
            pythoncom.CoInitialize()
            pdf_path = f'{nombre_archivo_final[:-5]}.pdf'
            print(f'El path es {pdf_path}')
            # Convertir a PDF
            convert(nombre_archivo_final, pdf_path)

            # Confirmar si se creó el archivo PDF
            if os.path.exists(pdf_path):
                # Leer el archivo PDF en un buffer
                buffer = io.BytesIO()
                with open(pdf_path, 'rb') as f:
                    buffer.write(f.read())
                buffer.seek(0)
                return pdf_path  # Devolver la ruta si todo fue bien
            else:
                print("Error: el archivo PDF no se generó.")
                return None  # Retorna None si no se generó el PDF

        except Exception as e:
            print(f"Error en la conversión a PDF: {e}")
            return None
        finally:
            # Liberar COM
            pythoncom.CoUninitialize()
    else:
        print(f"Error: el archivo .docx no existe en la ruta: {nombre_archivo_final}")
        return None