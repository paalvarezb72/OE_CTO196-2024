# docs/replace_data.py
from docx.shared import Pt

def reemplazar_datos_en_runs(paragraph, search_text, replace_text):
    text = paragraph.text
    if search_text in text:
        new_text = text.replace(search_text, replace_text)
        for run in paragraph.runs:
            run.text = ''
            run.font.name = 'Verdana'
            run.font.size = Pt(11)
        if paragraph.runs:
            paragraph.runs[0].text = new_text
        else:
            paragraph.add_run(new_text)

def reemplazar_datos_noEMC(doc, nombres, apellidos, correo, descrip_solicit, clickinfo):#, lat_pi, lon_pi):
    datos = {
        "{{NOMBRES}}": nombres.upper(),
        "{{APELLIDOS}}": apellidos.upper(),
        "{{CORREO}}": correo,
        "{{DESCRIP_SOLICIT}}": descrip_solicit,
        "{{LAT_PI}}": str(clickinfo[0]),#str(lat_pi),
        "{{LONG_PI}}": str(clickinfo[1])#str(lon_pi)
    }
    for p in doc.paragraphs:
        for key, value in datos.items():
            reemplazar_datos_en_runs(p, key, value)
    return doc

def reemplazar_datos_nan(doc, nombres, apellidos, correo, dias, meses, ano, selected_variable, estacion_seleccionada, descrip_solicit):
    datos = {
        "{{NOMBRES}}": nombres.upper(),
        "{{APELLIDOS}}": apellidos.upper(),
        "{{CORREO}}": correo,
        "{{DIAS}}": ", ".join(map(str, dias)),
        "{{MESES}}": ", ".join(meses),
        "{{AÑO}}": ", ".join(map(str, ano)),
        "{{VARIABLE}}": selected_variable,
        "{{ESTACION}}": estacion_seleccionada['nombre'],
        "{{DESCRIP_SOLICIT}}": descrip_solicit
    }
    for p in doc.paragraphs:
        for key, value in datos.items():
            reemplazar_datos_en_runs(p, key, value)
    return doc

def reemplazar_datos_precip(doc, nombres, apellidos, dias, meses, ano, selected_variable, estacion_seleccionada, dia, mes_nm, ano_p, primer_valor):
    datos = {
        "{{NOMBRES}}": nombres.upper(),
        "{{APELLIDOS}}": apellidos.upper(),
        "{{DIAS}}": ", ".join(map(str, dias)),
        "{{MESES}}": ", ".join(meses),
        "{{AÑO}}": ", ".join(map(str, ano)),
        "{{VARIABLE}}": selected_variable,
        "{{ESTACION}}": estacion_seleccionada['nombre'],
        "{{LATITUD}}": str(estacion_seleccionada['latitud']),
        "{{LONGITUD}}": str(estacion_seleccionada['longitud']),
        "{{ALTITUD}}": str(estacion_seleccionada['altitud']),
        "{{MUNICIPIO}}": str(estacion_seleccionada['MUNICIPIO']),
        "{{DEPARTAMENTO}}": str(estacion_seleccionada['DEPARTAMENTO']),
        "{{DIA}}": str(dia),
        "{{MES}}": str(mes_nm),
        "{{AÑO_P}}": str(ano_p),
        "{{PRIMER_DATO}}": str(primer_valor),
        "{{PRIMER_DATO_HA}}": str(primer_valor * 10),
    }

    for p in doc.paragraphs:
        for key, value in datos.items():
            reemplazar_datos_en_runs(p, key, value)

    return doc

def reemplazar_datos(doc, nombres, apellidos, dias, meses, ano, selected_variable, estacion_seleccionada):
    datos = {
        "{{NOMBRES}}": nombres.upper(),
        "{{APELLIDOS}}": apellidos.upper(),
        "{{DIAS}}": ", ".join(map(str, dias)) if dias else "",  # Manejar caso donde dias es None
        "{{MESES}}": ", ".join(meses) if meses else "",  # Manejar caso donde meses es None
        "{{AÑO}}": ", ".join(map(str, ano)), #if ano else "",  # Manejar caso donde ano es None
        "{{VARIABLE}}": selected_variable,
        "{{ESTACION}}": estacion_seleccionada['nombre'],
        "{{LATITUD}}": str(estacion_seleccionada['latitud']),
        "{{LONGITUD}}": str(estacion_seleccionada['longitud']),
        "{{ALTITUD}}": str(estacion_seleccionada['altitud']),
        "{{MUNICIPIO}}": str(estacion_seleccionada['MUNICIPIO']),
        "{{DEPARTAMENTO}}": str(estacion_seleccionada['DEPARTAMENTO']),
    }
    for p in doc.paragraphs:
        for key, value in datos.items():
            reemplazar_datos_en_runs(p, key, value)
    return doc
