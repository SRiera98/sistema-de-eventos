from sqlalchemy.exc import SQLAlchemyError
from errores import logger
from modelos import *
from flask import jsonify,request
from run import db,app,csrf
from funciones_mail import configurarYEnviarMail



#Listar Eventos Pendientes
#curl -H "Accept:application/json" http://localhost:8000/api/evento/listar/
@app.route('/api/evento/listar/',methods=['GET'])
def apiListarEventosPendientes():
    eventos=db.session.query(Evento).filter(Evento.aprobado==False)
    #Recorremos la lista de eventos no aprobados y convertimos cada uno a JSON para poder mostrarlas en la api.
    return jsonify({'eventos': [evento.a_json() for evento in eventos]})


#Editar Evento Pendiente
#curl -i -X PUT -H "Content-Type:application/json" -H "Accept:application/json" http://localhost:8000/api/evento_pendiente/editar/6 -d '{"nombre":"EventIA","fecha":"2020-01-03","hora":"18:30","tipo":"Curso"}'
@app.route('/api/evento_pendiente/editar/<id>',methods=['PUT'])
@csrf.exempt #Exceptuamos el uso del token de seguridad CSRF para permitir operar a la API
def apiActualizarEventoPendiente(id):
    evento = db.session.query(Evento).get_or_404(id)
    #El request.json.get lo que hace primero es buscar la clave que le indiquemos como primer parametro en el JSON del curl, si la encuentra ,
    # obtenemos su valor y lo igualamos al atributo del evento correspondiente, en caso contrario utiliza el segundo parametro que es el valor
    # por defecto que ya estaba seteado anteriormente.
    evento.nombre = request.json.get('nombre', evento.nombre)
    evento.fecha=request.json.get('fecha',evento.fecha)
    evento.hora=request.json.get('hora',evento.hora)
    evento.descripcion=request.json.get('descripcion',evento.descripcion)
    evento.tipo=request.json.get('tipo',evento.tipo)
    evento.aprobado=False
    db.session.add(evento)
    try:
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        logger(str(e._message()),"Funcion apiActualizarEventoPendiente in rutas_api.py")
    print("Evento fue actualizado con exito!")
    return jsonify(evento.a_json()), 201 #Convertimos el evento actualizado a JSON y indicamos con el status 201
                                         # que la operacion modifico el recurso (evento) con exito

#Eliminar Evento Pendiente
#curl -i -X DELETE -H "Accept:application/json" http://localhost:8000/api/evento_pendiente/eliminar/110
@app.route('/api/evento_pendiente/eliminar/<id>',methods=['DELETE'])
@csrf.exempt #Exceptuamos el uso del token de seguridad CSRF para permitir operar a la API
def apiEliminarEventoPendiente(id):
    evento=db.session.query(Evento).get_or_404(id)
    db.session.delete(evento)
    try:
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        logger(str(e._message()),"Funcion apiEliminarEventoPendiente in rutas_api.py")
    print("Evento fue eliminado con exito!")
    return "",204 #Retornamos el status 204, que indica que no hay contenido por retornar.

#Aprobar Evento
#curl -X POST -i -H "Content-Type:application/json" -H "Accept:application/json"  http://localhost:8000/api/evento_pendiente/aprobar/109
@app.route('/api/evento_pendiente/aprobar/<id>',methods=['POST'])
@csrf.exempt #Exceptuamos el uso del token de seguridad CSRF para permitir operar a la API
def apiAprobarEventoPendiente(id):
    evento=db.session.query(Evento).get_or_404(id)
    evento.aprobado=True
    configurarYEnviarMail(evento.usuario.email, '¡Tu Evento fue Aprobado!', 'mail/eventoaprobado', evento=evento) #Enviamos mail de aprobacion.
    db.session.add(evento)
    try:
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        logger(str(e._message()),"Funcion apiAprobarEventoPendiente in rutas_api.py")
    print("Evento fue aprobado con exito!")
    #Retornamos el evento que acabamos de aprobar en formato JSON
    return jsonify({'evento': [evento.a_json()]})


#listar Eventos por Id
#curl -i -H "Content-Type:application/json" -H "Accept: application/json" http://localhost:8000/api/evento/2
@app.route('/api/evento/<id>', methods=['GET'])
def apiGetEventoById(id):
    evento =  db.session.query(Evento).get_or_404(id)
    #Convertir el evento consultado en JSON
    return jsonify(evento.a_json())

#Listar Comentarios por Evento
#curl -H "Accept:application/json" http://localhost:8000/api/evento/comentarios/todos/108
@app.route('/api/evento/comentarios/todos/<id>',methods=['GET'])
def apiListarComentariosByEvento(id):
    comentarios=db.session.query(Comentario).filter(Comentario.eventoId==Evento.eventoId, Comentario.eventoId==id,Evento.eventoId==id)
    #retornamos todos los comentarios de un evento en particular en formato JSON
    return jsonify({'Comentarios': [comentario.a_json() for comentario in comentarios]})

#Eliminar Comentario
#curl -i -X DELETE -H "Accept:application/json" http://localhost:8000/api/comentario/eliminar/110
@app.route('/api/comentario/eliminar/<id>',methods=['DELETE'])
@csrf.exempt #Exceptuamos el uso del token de seguridad CSRF para permitir operar a la API
def apiEliminarComentario(id):
    comentario=db.session.query(Comentario).get_or_404(id)
    db.session.delete(comentario)
    try:
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        logger(str(e._message()),"Funcion apiEliminarComentario in rutas_api.py")
    print("Comentario Eliminado correctamente!")
    return "", 204 #Retornamos el status 204, que indica que no hay contenido por retornar.

#listar Comentario por Id
#curl -i -H "Content-Type:application/json" -H "Accept: application/json" http://localhost:8000/api/comentario/2
@app.route('/api/comentario/<id>', methods=['GET'])
def apiGetComentarioById(id):
    comentario =  db.session.query(Comentario).get_or_404(id)
    #Convertir el comentario consultado en JSON
    return jsonify(comentario.a_json())