from flask import render_template,request, jsonify
from run import app
import time
import datetime
"""En flask tenemos decoradores que sobreescriben comportamientos especificos."""
#Manejar error de página no encontrada

def logger(error,suceso):
    file = open("errores.log", 'a')
    file.write(f"\n{datetime.datetime.now()}, {error},Funcion {suceso},")
    file.close()


@app.errorhandler(404)
def page_not_found(e):
    print(str(e))
    #Si la solicitud acepta json y no HTML
    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
        #Responder con JSON
        response = jsonify({'error': 'not found'})
        response.status_code = 404
        return response
    #Sino responder con template HTML
    return render_template('errores/404.html'), 404

#Manejar error de error interno
@app.errorhandler(500)
def internal_server_error(e):
    print(e)
    logger(e,"Unknown")
    #Si la solicitud acepta json y no HTML
    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
        #Responder con JSON
        response = jsonify({'error': 'internal server error'})
        response.status_code = 500
        return response
    #Sino responder con template HTML
    return render_template('errores/500.html'), 500

def mostrarTemplateError():
    print("entro al TEMPLATE!")
    return render_template('errores/500.html')

