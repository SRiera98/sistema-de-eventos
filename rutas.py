from sqlalchemy.exc import SQLAlchemyError #Se encarga de indicarnos el error de SQL
from modelos import * #Importamos las clases que representan cada una de las tablas de nuestra Base de Datos
from flask import redirect, url_for,render_template #importar para permitir redireccionar y generar url ademas otro modulo para importar templates
from flask import flash #importar para mostrar mensajes flash
import os.path #Nos permitira guardar las imagenes que carguemos en nuestro sistema
from werkzeug.utils import secure_filename # Modifica el nombre del archivo a uno seguro
from datetime import datetime #manejo de fechas.
from run import db, app, login_manager
from random import randint #importa funcion random que sera utilizada para guardar imagen
from funciones_mail import *
from funciones_basedatos import * #Funciones para el envio de mail al usuario.
import formularios #Importamos las clases de los formularios, que luego seran instanciadas a su debido tiempo.
from flask_login import login_required, login_user, logout_user, current_user #Diferentes modulos de Flask para manejar Sesiones
from errores import *
from funciones import * #Funciones para los print de formularios que nos sirven para control.

#Es una funcion a la que se entra por defecto, cuando un usuario no logueado trata de acceder a una ruta login_required.
@login_manager.unauthorized_handler
def unauthorized_callback():
    flash('Debe iniciar sesión para continuar y realizar esa acción.','warning')
    #Redireccionar a la página que contiene el formulario de login
    return redirect(url_for('login'))


#Ruta que representa el Inicio de Sesion de la Web.
@app.route('/',methods=['POST','GET'])
def login():
    # Claramente no me puedo loguear estando ya logueado.
    if current_user.is_authenticated == True:
        return redirect(url_for('index'))

    ingreso=formularios.FormularioLogin()
    if ingreso.validate_on_submit():

        # Obterner usuario por email
        usuario = Usuario.query.filter_by(email=ingreso.email.data).first()

        # Si el usuario existe y se verifica la pass
        if usuario is not None and usuario.check_password(ingreso.contrasena.data):
            # Loguear usuario
            login_user(usuario,False) #El segundo parametro indica que no se utilizara la funcionalidad "Remember Me"
            username = ingreso.email.data
            flash('¡ Bienvenido {}!'.format(username))
            mostrar_datos_login(ingreso)
            return redirect(url_for('index'))
        else:
            #Mostrar error de autenticación
            flash('Email o pass incorrectas.','success')

    return render_template('iniciar_sesion.html',ingresar=ingreso)


#Logout - Deslogueo de usuario.
@app.route('/logout')
#Limitar el acceso a los usuarios registrados
@login_required #Metodo de Flask Login del LoginManager que permite darle a los usuarios acceso restringido a ciertas vistas.
def logout():
    logout_user()
    return redirect(url_for('login'))

#Representa la Pagina principal, donde veremos los diferentes Eventos de los usuarios.
@app.route('/index')
#Ruta a la que se ingresa cuando se pagina sin filtro
@app.route('/index/<int:pag>',methods=['GET'])
#Ruta a la que se ingresa cuando se pagina con filtros ya aplicados
@app.route('/index/<int:pag>/<desde_fecha>/<hasta_fecha>/<categoria>',methods=['GET'])
def index(pag=1, desde_fecha='', hasta_fecha='', categoria=''):
    #Instancio formulario de filtrado
    formulario=formularios.FormularioFiltrarEvento()
    tam_pag = 6 #Indicamos el numero de elementos por pagina.

    #Si se realiza la búsqueda por formulario de filtro
    # Con request.args creamos un diccionario con los argumentos del formulario, luego vamos buscando coincidencias con
    # la clave del diccionario, en cada coincidencia se verifica que no este vacio el valor de la clave del diccionario
    #Si lo esta asignamos None(NULL) a la variable.
    if(request.args): #request.args crea un diccionario con los argumentos enviados en el formulario.
        desde_fecha = request.args.get('desde_fecha',None)
        hasta_fecha = request.args.get('hasta_fecha',None)
        categoria = request.args.get('categoria',None)
    listaeventos = Evento.query.filter(Evento.aprobado==True)
    #Si se filtra por fecha desde cargar el valor en el formulario convirtiendo el valor de string a fecha
    if(desde_fecha!=None and desde_fecha!=''):
        formulario.desde_fecha.data = datetime.datetime.strptime(desde_fecha, "%Y-%m-%d").date()
        listaeventos=listaeventos.filter(Evento.fecha>=desde_fecha)
    #Si se filtra por fecha hasta cargar el valor en el formulario convirtiendo el valor de string a fecha
    if(hasta_fecha!=None and hasta_fecha!=''):
        formulario.hasta_fecha.data = datetime.datetime.strptime(hasta_fecha, "%Y-%m-%d").date()
        listaeventos=listaeventos.filter(Evento.fecha<=hasta_fecha)
    #Si se filtra por categoria desde cargar el valor en el formulario
    if(categoria!=None and categoria!=''  and categoria!='null' and categoria!='None'):
        formulario.categoria.data = categoria
        listaeventos=listaeventos.filter(Evento.tipo==categoria)
    listaeventos=listaeventos.order_by(Evento.fecha.asc())
    listaeventos=listaeventos.paginate(pag,tam_pag,error_out=False)
    return render_template('index_usuario.html',listar_eventos=listaeventos,formulario=formulario)


@app.route('/usuario/crear-evento',methods=['POST','GET'])
@login_required #Metodo de Flask Login del LoginManager que permite darle a los usuarios acceso restringido a ciertas vistas.
def establecer_evento():
    #Instancio formulario para crear un evento
    nuevoevento=formularios.FormularioCrearEvento()
    #Verifico si el formulario ha sido enviado
    if nuevoevento.validate_on_submit():
        file = nuevoevento.imagen.data  # Obtener imagen
        filename = secure_filename(nuevoevento.titulo.data + " imagen " +str(randint(1,2000)))  # Modifica el nombre del archivo a uno seguro
        file.save(os.path.join('static/imagenes/', filename))  # Guardar imagen en sistema
        flash('¡Evento creado correctamente!')
        mostrar_datos_nuevoevento(nuevoevento)
        #Creamos el evento llamando a la funcion dedicada para ello.
        evento=crearEvento(nuevoevento.titulo.data,nuevoevento.fecha.data,nuevoevento.hora.data,nuevoevento.descripcion.data,filename,nuevoevento.opciones.data,current_user.usuarioId)

        #Si hubieron errores al crear el evento, retornamos el template correspondiente.
        if evento==False:
            return mostrarTemplateError()
        return redirect(url_for('eventos_usuario'))
    return render_template('establecer_evento.html',agregarevento=nuevoevento,destino="establecer_evento")



@app.route('/usuario/evento/actualizar/<id>',methods=['POST','GET'])
@login_required #Metodo de Flask Login del LoginManager que permite darle a los usuarios acceso restringido a ciertas vistas.
def actualizar_evento(id):

    #Traemos el evento a modificar con determinado id
    evento=db.session.query(Evento).get(id)
    #Instanciamos el formulario
    nuevoevento = formularios.FormularioCrearEvento(obj=evento)

    #Verificamos si el formulario ha sido enviado, nuestra condicion no se cumplira en principio, y esto nos permitira que carguemos los datos
    # actuales del evento al formulario para posteriormente modificarlos, enviar el formulario, volver a entrar en nuestra funcion y complir nuestra condicion de formulario enviado.

    if nuevoevento.validate_on_submit():
        flash('¡Evento actualizado correctamente!')
        mostrar_datos_nuevoevento(nuevoevento)
        evento.nombre=nuevoevento.titulo.data           # A los valores de la query del objeto que queremos le asignamos los nuevos conseguidos por el propio formulario
        evento.fecha=nuevoevento.fecha.data
        evento.hora=nuevoevento.hora.data
        evento.descripcion=nuevoevento.descripcion.data
        evento.tipo=nuevoevento.opciones.data
        evento.imagen=nuevoevento.imagen.data
        if current_user.admin:                 #Vericamos si el que lo actualiza es el admin,
            evento.aprobado = evento.aprobado  # ya que no tendria sentido que el admin vuelva a aprobar el evento del admin
        else:                                  #Si es admin se mantendra el valor de BD , si no se desaprobara el evento al actualizar.
            evento.aprobado=False
        actualizacion=actualizarEvento(evento)
        if actualizacion==False:
            return mostrarTemplateError()
        if not current_user.admin:
            return redirect(url_for('eventos_usuario'))
        else:
            return redirect(url_for('indexadmin'))
    else:

        nuevoevento.titulo.data = evento.nombre
        nuevoevento.fecha.data = evento.fecha
        nuevoevento.hora.data = evento.hora
        nuevoevento.descripcion.data = evento.descripcion
        nuevoevento.opciones.data = evento.tipo
        nuevoevento.imagen.data = evento.imagen

        formularios.FormularioCrearEvento.opcional(nuevoevento.imagen)
        return render_template('establecer_evento.html',agregarevento=nuevoevento,destino="actualizar_evento",evento=evento)



@app.route('/admin/evento-detallado/<id>',methods=['POST','GET'])
@login_required #Metodo de Flask Login del LoginManager que permite darle a los usuarios acceso restringido a ciertas vistas.
def evento_en_detalle_admin(id):
    comentario=formularios.FormularioComentario()
    #Verifico si el usuario que accedio a esta ruta es Admin, si no lo es, lo redirijo a la pagina principal.
    if current_user.is_admin()==False:
        flash('¡No tienes permisos para acceder a esta ruta!')
        return redirect(url_for('index'))
    evento = db.session.query(Evento).get(id)
    return render_template('evento_detallado_admin.html',evento=evento,comentario=comentario)

@app.route('/index/evento/<id>',methods=["POST","GET"])
def eventogeneral(id):
    #Instancio formulario de comentario...
    nuevocomentario=formularios.FormularioComentario()

    #instancio evento por id
    evento=db.session.query(Evento).get(id)

    return render_template('evento_general.html',evento=evento,nuevocomentario=nuevocomentario)


@app.route('/index/evento/agregar-comentario/<id>',methods=["POST"])
@login_required #Metodo de Flask Login del LoginManager que permite darle a los usuarios acceso restringido a ciertas vistas.
def agregar_comentario(id):
    nuevocomentario = formularios.FormularioComentario()
    if nuevocomentario.validate_on_submit():
        mostrar_datos_comentario(nuevocomentario)
        #Creo un nuevo comentario a partir de los datos enviados por el formulario (FormularioComentario)
        comentario=crearComentario(contenido=nuevocomentario.comentario.data,usuarioId=current_user.usuarioId,eventoId=id)

        #Verifico si ha sucedido un error al crear el comentario.
        if comentario==False:
            return mostrarTemplateError()

        flash('¡Has comentado el evento con exito!')
        #Si el usuario comento correctamente, sera redirigido nuevamente al evento donde estaba comentando.
        return redirect(url_for('eventogeneral',id=id))
    return render_template('evento_general.html',nuevocomentario=nuevocomentario)

@app.route('/usuario/eventos/mostrar')
@login_required #Metodo de Flask Login del LoginManager que permite darle a los usuarios acceso restringido a ciertas vistas.
def eventos_usuario():
    #Hago un query (consulta a la BD) para obtener todos los eventos propios del usuario actual.
    listaeventos=db.session.query(Evento).filter(Evento.usuarioId==current_user.usuarioId).all()
    return render_template('panel_usuario.html',listar_eventos=listaeventos)

@app.route('/admin')
@login_required #Metodo de Flask Login del LoginManager que permite darle a los usuarios acceso restringido a ciertas vistas.
def indexadmin():
    # Verifico si el usuario que accedio a esta ruta es Admin, si no lo es, lo redirijo a la pagina principal.
    if current_user.is_admin()==False:
        flash('¡No tienes permisos para acceder a esta ruta!')
        return redirect(url_for('index'))
    lista_eventos_aprobados=db.session.query(Evento).filter(Evento.aprobado==True).all()
    lista_eventos_pendientes = db.session.query(Evento).filter(Evento.aprobado == False).all()
    return render_template('index_admin.html',lista_eventos_aprobados=lista_eventos_aprobados,lista_eventos_pendientes=lista_eventos_pendientes,evento="pendiente")

@app.route('/admin/evento/aprobar/<id>')
@login_required #Metodo de Flask Login del LoginManager que permite darle a los usuarios acceso restringido a ciertas vistas.
def aprobar_evento(id):
    # Verifico si el usuario que accedio a esta ruta es Admin, si no lo es, lo redirijo a la pagina principal.
    if current_user.is_admin()==False:
        flash('¡No tienes permisos para acceder a esta ruta!')
        return redirect(url_for('index'))
    evento=db.session.query(Evento).get(id)
    evento.aprobado=True
    actualizacion = actualizarEvento(evento)
    if actualizacion == False:
        return mostrarTemplateError()
    #Estableciendo todo para enviar email
    email=evento.usuario.email
    # Crear hilo para enviar mail asincronico
    # Destino, Asunto, Template
    configurarYEnviarMail(email, '¡Tu Evento fue Aprobado!', 'eventoaprobado',evento=evento)
    return redirect(url_for('indexadmin',evento=evento))

@app.route('/iniciar-sesion/registrarse',methods=["POST","GET"])
def registro_usuario():
    #Claramente no me puedo registrar estando ya logueado.
    if current_user.is_authenticated==True:
        return redirect(url_for('index'))
    registro=formularios.FormularioRegistro()
    if registro.validate_on_submit(): #Si el formulario ha sido enviado y es validado correctamente
        username=registro.nombre.data

        mostrar_datos(registro)  #Imprimir datos por consola
        # Crear un usuario llamando a la funcion de BD
        usuario=crearUsuario(registro.nombre.data, registro.apellido.data, registro.email.data,registro.contrasena.data,False)

        if usuario==False:
            return mostrarTemplateError()

        flash('¡{} has sido registrado exitosamente!'.format(username))  # Mostrar mensaje de bienvenida
        #Establezco los parametros para enviar el email que confirma el registro
        # Destino, Asunto, Template
        configurarYEnviarMail(registro.email.data, '¡Gracias por Registrarte!', 'usuarioregistrado')
        return redirect(url_for('login'))
    return render_template('formulario_registro.html',registrar=registro)



#----------------Comienzo de algunas funciones de Base de Datos-------

@app.route('/evento/eliminar/<id>')
def eliminarEvento(id):

    # EJ: evento/eliminar/1
    #Obtener evento por id
    evento = db.session.query(Evento).get(id)
    # Traemos el usuarioId perteneciente a ese evento.
    usuarioId = evento.usuarioId
    if current_user.admin or (not current_user.admin and current_user.is_authenticated and current_user.usuarioId == usuarioId):

        #Eliminar de la db
        db.session.delete(evento)
        #Hacer commit de los cambios
        try:
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            logger(str(e._message()),"Funcion EliminarEventoAdmin in rutas.py")
            return mostrarTemplateError()
        if current_user.admin: #Verifico donde voy a redirigir cuando elimine el evento.
            return redirect(url_for('indexadmin', evento=evento))
        if not current_user.admin and current_user.is_authenticated and current_user.usuarioId==usuarioId:  #En caso de que no sea admin el usuario,
            return redirect(url_for('eventos_usuario', evento=evento))# verificamos que el evento sea suyo, en caso de que quiera borrar por URL

    else:
        flash('¡No puedes eliminar un evento que no es tuyo!')
        return redirect(url_for('index'))

#----------------------------------------------------------------------------


@app.route('/comentario/eliminar/<id>')
def eliminarComentario(id):

    # EJ: comentario/eliminar/1
    #Obtener comentario por id
    comentario = db.session.query(Comentario).get(id)
    #Traemos el usuarioId perteneciente a ese comentario.
    usuarioId=comentario.usuario.usuarioId
    #Obtenemos el eventoId asociado a ese comentario por medio de las relaciones de BD
    eventoid=comentario.eventoId
    if current_user.admin or (not current_user.admin and current_user.is_authenticated and current_user.usuarioId == usuarioId):

        #Eliminar de la db
        db.session.delete(comentario)
        #Hacer commit de los cambios
        try:
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            logger(str(e._message()),"Funcion eliminarComentario in rutas.py")
            return mostrarTemplateError()
        if current_user.admin:
            return redirect(url_for('evento_en_detalle_admin',id=eventoid))
        if not current_user.admin and current_user.is_authenticated and current_user.usuarioId==usuarioId: #En caso de que no sea admin el usuario,
            return redirect(url_for('eventogeneral', id=eventoid))                                          # verificamos que el comentario sea suyo, en caso de que quiera borrar por URL

    else:
        flash('¡No puedes eliminar un comentario que no es tuyo!')
        return redirect(url_for('index'))

@app.route('/comentario/eliminar/todos/<id>')
def eliminarTodosLosComentarios(id):
    # Verifico si el usuario que accedio a esta ruta es Admin, si no lo es, lo redirijo a la pagina principal.
    if current_user.is_admin() == False:
        flash('¡No tienes permisos para acceder a esta ruta!')
        return redirect(url_for('index'))

    #Instanciamos el evento deseado.
    evento=db.session.query(Evento).get(id)
    #Traemos todos los comentarios de dicho evento, debido a que para ello deberan coincidir los eventoId de evento y comentarios
    comentarios=db.session.query(Comentario).filter(Comentario.eventoId==evento.eventoId).all()
    # Eliminar de la db todos los comentarios del evento
    for datos in range(0,len(comentarios)):
        db.session.delete(comentarios[datos])
    # Hacer commit de los cambios
    try:
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        logger(str(e._message()),"Funcion eliminarTodosLosComentarios in rutas.py")
        return mostrarTemplateError()
    return redirect(url_for('indexadmin'))

#----------------Final de algunas funciones de Base de Datos-------




