from run import db
from modelos import *
from sqlalchemy.exc import SQLAlchemyError
from errores import logger


#----------------Comienzo de funciones de Base de Datos-------


def crearUsuario(nombre,apellido,email,password,admin=False):
    # Crear un usuario
    usuario = Usuario(nombre=nombre,apellido=apellido, email=email,passwrd=password, admin=admin)
    # Agregar a db
    db.session.add(usuario)
    # Hacer commit de los cambios
    try:
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        logger(str(e._message()),"Funcion crearUsuario in funciones_basedatos.py")
        return False
    return usuario

#------------------------------------------------------------------------------


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


def actualizarEvento(evento):
    db.session.add(evento)
    try:
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        logger(str(e._message()),"Funcion actualizarEvento in funciones_basedatos.py")
        return False


#----------------------------------------------------------------------------


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

#----------------Final de funciones de Base de Datos-------""""""