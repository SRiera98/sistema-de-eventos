from modelos import *
from flask import request
from flask import Flask
import formularios
from dotenv import load_dotenv #carga las variables de entorno
import os
from flask import redirect, url_for #importar para permitir redireccionar y generar url
from flask import flash #importar para mostrar mensajes flash
import os.path
from werkzeug.utils import secure_filename
import datetime
from datetime import datetime
from flask import render_template #Permite importar templates
from flask import redirect, url_for #importar para permitir redireccionar y generar url
from run import db,app
import datetime #importar funciones de fecha
from funciones_mail import *
from funciones_basedatos import *
from flask_login import login_required, login_user, logout_user, current_user, LoginManager
load_dotenv()
def mysql_query(query):
    return query.statement.compile(compile_kwargs={"literal_binds": True})

def mostrar_datos(registro):
    print(registro.nombre.data)
    print(registro.apellido.data)
    print(registro.email.data)
    print(registro.contrasena.data)
def mostrar_datos_login(ingreso):
    print(ingreso.email.data)
    print(ingreso.contrasena.data)
def mostrar_datos_nuevoevento(nuevoevento):
    print(nuevoevento.titulo.data)
    print(nuevoevento.fecha.data)
    print(nuevoevento.hora.data)
    print(nuevoevento.opciones.data)
    print(nuevoevento.descripcion.data)
    print(nuevoevento.imagen.data)
def mostrar_datos_comentario(nuevocomentario):
    print(nuevocomentario.comentario.data)

def mostrar_datos_filtrado(formulario):
    print("Fechadesde"+str(formulario.desde_fecha.data))
    print("Fechahasta"+str(formulario.hasta_fecha.data))
    print("Categoria"+str(formulario.categoria.data))



app.secret_key = os.getenv('SECRET_KEY') #clave secreta

@login_manager.unauthorized_handler #es una funcion por defecto, para las funcion login required.
def unauthorized_callback():
    flash('Debe iniciar sesión para continuar.','warning')
    #Redireccionar a la página que contiene el formulario de login
    return redirect(url_for('login'))
"""
#Se ejecuta cada vez que se realiza una request
@app.before_request #una funcion que se va a ejecutar antes de entrar a cualquier funcion de una ruta.
def before_request():
    #Si el usuario no esta logueado
    usuario = current_user
    if usuario.is_authenticated==False and request.endpoint!="login" and request.endpoint!="registro_usuario":
        ingreso = formularios.FormularioLogin() #instancio el formulario de login debido a que se lo necesito pasar al template
        return render_template('iniciar_sesion.html',ingresar=ingreso)
"""


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
            login_user(usuario,False)
            username = ingreso.email.data
            flash('¡ Bienvenido {}!'.format(username))
            mostrar_datos_login(ingreso)
            return redirect(url_for('index'))
        else:
            #Mostrar error de autenticación
            flash('Email o pass incorrectas.','success')

    return render_template('iniciar_sesion.html',ingresar=ingreso)


#Logout
@app.route('/logout')
#Limitar el acceso a los usuarios registrados
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/index')
#Ruta a la que se ingresa cuando se pagina sin filtro
@app.route('/index/<int:pag>',methods=['GET'])
#Ruta a la que se ingresa cuando se pagina con filtros ya aplicados
@app.route('/index/<int:pag>/<desde_fecha>/<hasta_fecha>/<categoria>',methods=['GET'])
@login_required
def index(pag=1, desde_fecha='', hasta_fecha='', categoria=''):
    #Instancio formulario de filtrado
    formulario=formularios.FormularioFiltrarEvento()
    tam_pag = 6
    #Si se realiza la búsqueda por formulario de filtro
    if(request.args):
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
@login_required
def establecer_evento():
    nuevoevento=formularios.FormularioCrearEvento()
    if nuevoevento.validate_on_submit():
        file = nuevoevento.imagen.data  # Obtener imagen
        filename = secure_filename(file.filename)  # Modifica el nombre del archivo a uno seguro
        file.save(os.path.join('static/imagenes/', filename))  # Guardar imagen en sistema
        flash('¡Evento creado correctamente!')
        mostrar_datos_nuevoevento(nuevoevento)
        #crearEvento(nombre,fecha,hora,descripcion,imagen,tipo,usuarioId):
        crearEvento(nuevoevento.titulo.data,nuevoevento.fecha.data,nuevoevento.hora.data,nuevoevento.descripcion.data,filename,nuevoevento.opciones.data,current_user.usuarioId)
        return redirect(url_for('establecer_evento'))
    return render_template('establecer_evento.html',agregarevento=nuevoevento,destino="establecer_evento")



@app.route('/usuario/evento/actualizar/<id>',methods=['POST','GET'])
@login_required
def actualizar_evento(id):

    #Traemos el evento a modificar con determinado id
    evento=db.session.query(Evento).get(id)
    #Instanciamos el formulario
    nuevoevento = formularios.FormularioCrearEvento(obj=evento)

    #creo variable usuario para cambiar de cabecera

    if nuevoevento.validate_on_submit():
        flash('¡Evento actualizado correctamente!')
        mostrar_datos_nuevoevento(nuevoevento)
        evento.nombre=nuevoevento.titulo.data
        evento.fecha=nuevoevento.fecha.data
        evento.hora=nuevoevento.hora.data
        evento.descripcion=nuevoevento.descripcion.data
        evento.tipo=nuevoevento.opciones.data
        evento.imagen=nuevoevento.imagen.data
        evento.aprobado=False

        actualizarEvento(evento)
    else:

        nuevoevento.titulo.data = evento.nombre
        nuevoevento.fecha.data = evento.fecha
        nuevoevento.hora.data = evento.hora
        nuevoevento.descripcion.data = evento.descripcion
        nuevoevento.opciones.data = evento.tipo
        nuevoevento.imagen.data = evento.imagen

        formularios.FormularioCrearEvento.opcional(nuevoevento.imagen)
    return render_template('establecer_evento.html',agregarevento=nuevoevento,destino="actualizar_evento",evento=evento)



@app.route('/admin/evento-detallado/<id>')
@login_required
def evento_en_detalle_admin(id):
    #Verifico si el usuario que accedio a esta ruta es Admin, si no lo es, lo redirijo a la pagina principal.
    if current_user.is_admin()==False:
        return redirect(url_for('index'))
    evento = db.session.query(Evento).get(id)
    return render_template('evento_detallado_admin.html',evento=evento)

@app.route('/index/evento/<id>',methods=["POST","GET"])
def eventogeneral(id):
    #Comienzo de formularios COMENTARIOS...
    nuevocomentario=formularios.FormularioComentario()

    #instancio evento por id
    evento=db.session.query(Evento).get(id)

    return render_template('evento_general.html',evento=evento,nuevocomentario=nuevocomentario)


@app.route('/index/evento/agregar-comentario/<id>',methods=["POST"])
@login_required
def agregar_comentario(id):
    nuevocomentario = formularios.FormularioComentario()
    if nuevocomentario.validate_on_submit():
        flash('¡Has comentado el evento con exito!')
        mostrar_datos_comentario(nuevocomentario)
        crearComentario(contenido=nuevocomentario.comentario.data,usuarioId=current_user.usuarioId,eventoId=id)
        return redirect(url_for('eventogeneral',id=id))
    return render_template('evento_general.html',nuevocomentario=nuevocomentario)

@app.route('/usuario/eventos/mostrar')
@login_required
def eventos_usuario():
    listaeventos=db.session.query(Evento).filter(Evento.usuarioId==current_user.usuarioId).all()
    return render_template('panel_usuario.html',listar_eventos=listaeventos)

@app.route('/admin')
@login_required
def indexadmin():
    # Verifico si el usuario que accedio a esta ruta es Admin, si no lo es, lo redirijo a la pagina principal.
    if current_user.is_admin()==False:
        return redirect(url_for('index'))
    lista_eventos_aprobados=db.session.query(Evento).filter(Evento.aprobado==True).all()
    lista_eventos_pendientes = db.session.query(Evento).filter(Evento.aprobado == False).all()
    return render_template('index_admin.html',lista_eventos_aprobados=lista_eventos_aprobados,lista_eventos_pendientes=lista_eventos_pendientes,evento="pendiente")

@app.route('/admin/evento/aprobar/<id>')
@login_required
def aprobar_evento(id):
    # Verifico si el usuario que accedio a esta ruta es Admin, si no lo es, lo redirijo a la pagina principal.
    if current_user.is_admin()==False:
        return redirect(url_for('index'))
    evento=db.session.query(Evento).get(id)
    evento.aprobado=True
    actualizarEvento(evento)

    #Estableciendo todo para enviar email
    email=evento.usuario.email
    # Crear hilo para enviar mail asincronico
    # Destino, Asunto, Template
    enviarMailThread(email, '¡Tu Evento fue Aprobado!', 'mail/eventoaprobado',evento=evento)
    return redirect(url_for('indexadmin',evento=evento))

@app.route('/iniciar-sesion/registrarse',methods=["POST","GET"])
def registro_usuario():
    #Claramente no me puedo registrar estando ya logueado.
    if current_user.is_authenticated==True:
        return redirect(url_for('index'))
    registro=formularios.FormularioRegistro()
    if registro.validate_on_submit(): #Si el formulario ha sido enviado y es validado correctamente
        username=registro.nombre.data
        flash('¡{} has sido registrado exitosamente!'.format(username)) #Mostrar mensaje
        mostrar_datos(registro)  #Imprimir datos por consola
        # Crear un usuario
        usuario=crearUsuario(registro.nombre.data, registro.apellido.data, registro.email.data,registro.contrasena.data,False)

        #Establezco los parametros para enviar el email que confirma el registro
        # Crear hilo para enviar mail asincronico
        # Destino, Asunto, Template
        enviarMailThread(registro.email.data, '¡Gracias por Registrarte!', 'mail/usuarioregistrado')
        return redirect(url_for('index'))
    return render_template('formulario_registro.html',registrar=registro)



#----------------Comienzo de algunas funciones de Base de Datos-------

@app.route('/evento/eliminar/<id>')
def eliminarEventoAdmin(id):
    # Verifico si el usuario que accedio a esta ruta es Admin, si no lo es, lo redirijo a la pagina principal.
    if current_user.is_admin() == False:
        return redirect(url_for('index'))
    # EJ: evento/eliminar/1
    #Obtener evento por id
    evento = db.session.query(Evento).get(id)
    #Eliminar de la db
    db.session.delete(evento)
    #Hacer commit de los cambios
    db.session.commit()
    return redirect(url_for('indexadmin', evento=evento))


@app.route('/usuario/evento/eliminar/<id>')
def eliminarEventoUser(id):
    # EJ: evento/eliminar/1
    #Obtener evento por id
    evento = db.session.query(Evento).get(id)
    #Eliminar de la db
    db.session.delete(evento)
    #Hacer commit de los cambios
    db.session.commit()
    return redirect(url_for('eventos_usuario', evento=evento))


#----------------------------------------------------------------------------


@app.route('/comentario/eliminar/<id>')
def eliminarComentario(id):
    # Verifico si el usuario que accedio a esta ruta es Admin, si no lo es, lo redirijo a la pagina principal.
    if current_user.is_admin() == False:
        return redirect(url_for('index'))

    # EJ: comentario/eliminar/1
    #Obtener comentario por id
    comentario = db.session.query(Comentario).get(id)
    eventoid=comentario.eventoId
    #Eliminar de la db
    db.session.delete(comentario)
    #Hacer commit de los cambios
    db.session.commit()
    return redirect(url_for('evento_en_detalle_admin',id=eventoid))

@app.route('/comentario/eliminar/todos/<id>')
def eliminarTodosLosComentarios(id):
    # Verifico si el usuario que accedio a esta ruta es Admin, si no lo es, lo redirijo a la pagina principal.
    if current_user.is_admin() == False:
        return redirect(url_for('index'))

    #Instanciamos el evento desado.
    evento=db.session.query(Evento).get(id)
    #Traemos todos los comentarios de dicho evento, debido a que para ello deberan coincidir los eventoId de evento y comentarios
    comentarios=db.session.query(Comentario).filter(Comentario.eventoId==evento.eventoId).all()
    # Eliminar de la db
    for datos in range(0,len(comentarios)):
        db.session.delete(comentarios[datos])
    # Hacer commit de los cambios
    db.session.commit()
    return redirect(url_for('indexadmin'))

#----------------Final de algunas funciones de Base de Datos-------




