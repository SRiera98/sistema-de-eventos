from flask import render_template,request, jsonify
from run import app
import datetime
"""En flask tenemos decoradores que sobreescriben comportamientos especificos."""
#Manejar error de página no encontrada

#Definimos una funcion que simula un logger, donde lo unico que hace es recibir el error sucedido y en donde sucedio ese error.
def logger(error,suceso):
    #Abrimos un archivo errores.log con tipo de apertura append (añadir), si no existe se creara, si existe se añadira al final del archivo.
    file = open("errores.log", 'a')
    file.write(f"\n{datetime.datetime.now()}, {error},Funcion {suceso},")
    file.close()

#Manejamos error de pagina no encontrada.
@app.errorhandler(404)
def page_not_found(e):
    logger(e, "Unknown")
    #Si la solicitud acepta json y no HTML
    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
        #Responder con JSON
        response = jsonify({'error': 'not found'})
        response.status_code = 404
        return response
    #Sino responder con template HTML
    return render_template('errores/404.html'), 404

#Manejamos error interno
@app.errorhandler(500)
def internal_server_error(e):
    logger(e,"Unknown")
    #Si la solicitud acepta json y no HTML
    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
        #Responder con JSON
        response = jsonify({'error': 'internal server error'})
        response.status_code = 500
        return response
    #Sino responder con template HTML
    return render_template('errores/500.html'), 500

#Simplemente es un metodo que retorna un template que representa un error.
def mostrarTemplateError():
    return render_template('errores/500.html')

