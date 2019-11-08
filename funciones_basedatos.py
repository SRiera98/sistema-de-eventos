from run import db,app
from flask import render_template,redirect, url_for
from flask import Flask
from modelos import *
from sqlalchemy.exc import SQLAlchemyError
from errores import logger, mostrarTemplateError


#----------------Comienzo de funciones de Base de Datos-------
@app.route('/usuario/list')
def listarUsuarios():
    # EJ: usuario/list
    usuarios = db.session.query(Usuario).all() #Trae todo de usuarios
    return render_template('usuarios.html',usuarios=usuarios,filtro="")

@app.route('/usuario/crear/<nombre>/<apellido>/<email>/<password>/<admin>')
def crearUsuario(nombre,apellido,email,password,admin=False):
    # Crear un usuario
    usuario = Usuario(nombre=nombre,apellido=apellido, email=email,passwrd=password, admin=admin)
    print(f"EL nombre es{usuario.nombre}")
    print(usuario)
    # Agregar a db
    db.session.add(usuario)
    # Hacer commit de los cambios
    try:
        db.session.commit()
        print("Commiteando.......\n\n\n")
    except SQLAlchemyError as e:
        print("Entrando a except.")
        db.session.rollback()
        logger(str(e._message()),"Funcion crearUsuario in funciones_basedatos.py")
        return False
    print("RETORNANDO USUARIO......")
    return usuario
    #Envía la persona a la vista
    #return render_template('index',usuario=usuario)

@app.route('/usuario/eliminar/<id>')
def eliminarUsuario(id):
    # EJ: usuario/eliminar/1
    #Obtener usuario por id
    usuario = db.session.query(Usuario).get(id)
    #Eliminar de la db
    db.session.delete(usuario)
    #Hacer commit de los cambios
    try:
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        logger(str(e._message()),"Funcion EliminarUsuario in funciones_basedatos.py")
        return mostrarTemplateError()
    return redirect(url_for('listarUsuarios'))

@app.route('/usuario/getById/<id>')
def getUsuarioById(id):
    # EJ: usuario/getById/2
    # Filtra por id
    usuario =  db.session.query(Usuario).get(id) #Busca el usuario con ese id
    #Envía el usuario a la vista
    return render_template('usuario.html',usuario=usuario)

#------------------------------------------------------------------------------

@app.route('/evento/list')
def listarEventos():
    # EJ: evento/list
    eventos = db.session.query(Evento).all() #Trae todo de eventos
    return render_template('eventos.html',eventos=eventos,filtro="")

@app.route('/evento/crear/<nombre>/<fecha>/<hora>/<descripcion>/<imagen>/<tipo>/<usuarioId>')
def crearEvento(nombre,fecha,hora,descripcion,imagen,tipo,usuarioId,aprobado=False):
    #Instancio usuario a asociar con evento.
    usuario=db.session.query(Usuario).get(usuarioId)
    #Crear un evento
    evento = Evento(usuario=usuario,nombre=nombre, fecha=fecha,hora=hora,descripcion=descripcion,imagen=imagen,tipo=tipo,aprobado=aprobado)
    #Agregar a db
    db.session.add(evento)
    #Hacer commit de los cambios
    try:
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        logger(str(e._message()),"Funcion crearEvento in funciones_basedatos.py")
        return False
    #Envía la persona a la vista
#    return render_template('evento.html',evento=evento)

@app.route('/evento/actualizar/<evento>')
def actualizarEvento(evento):
    db.session.add(evento)
    try:
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        logger(str(e._message()),"Funcion actualizarEvento in funciones_basedatos.py")
        return False



@app.route('/evento/getById/<id>')
def getEventoById(id):
    # EJ: evento/getById/2
    # Filtra por id
    evento =  db.session.query(Evento).get(id) #Busca el evento con ese id
    #Envía el evento a la vista
    return render_template('evento.html',evento=evento)

#----------------------------------------------------------------------------

@app.route('/comentario/list')
def listarComentarios():
    # EJ: comentario/list
    comentarios = db.session.query(Comentario).all() #Trae todo de comentarios
    return render_template('comentarios.html',comentarios=comentarios,filtro="")

@app.route('/comentario/crear/<contenido>/<usuarioId>/<eventoId>')
def crearComentario(contenido,usuarioId,eventoId):
    usuario=db.session.query(Usuario).get(usuarioId)
    evento=db.session.query(Evento).get(eventoId)
    fechahora=db.func.current_timestamp()
    #"2019-09-03 19:30"
    #Crear un comentario
    comentario = Comentario(contenido=contenido, fechahora=fechahora,evento=evento,usuario=usuario)
    #Agregar a db
    db.session.add(comentario)
    #Hacer commit de los cambios
    try:
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        logger(str(e._message()),"Funcion crearComentario in funciones_basedatos.py")
        return False
    #Envía el comentario a la vista
    #return render_template('comentario.html',comentario=comentario)


@app.route('/comentario/getById/<id>')
def getComentarioById(id):
    # EJ: comentario/getById/2
    # Filtra por id
    comentario =  db.session.query(Comentario).get(id) #Busca el comentario con ese id
    #Envía el comentario a la vista
    return render_template('comentario.html',comentario=comentario)
#----------------Final de funciones de Base de Datos-------""""""