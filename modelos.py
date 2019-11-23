from run import db,app,login_manager
from werkzeug.security import generate_password_hash, check_password_hash #Permite generar y verificar pass con hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer #enlace para confirmacion de registro
from flask_login import UserMixin, LoginManager
from flask import url_for

#Creamos una clase que representara una tabla en la Base de Datos, en este caso "evento", donde tendremos de Clave Principal o primaria a el id del evento
#declaramos los distintos campos de la tabla, cuales son sus tipos de datos, si pueden ser nulos  y algunos valores por default.
class Evento(db.Model):
    eventoId=db.Column(db.Integer, primary_key=True)
    nombre=db.Column(db.String(60),nullable=False)
    fecha=db.Column(db.Date,nullable=False)
    hora = db.Column(db.Time, nullable=False)
    descripcion=db.Column(db.String(500),nullable=True)
    imagen=db.Column(db.String(40),nullable=False)
    tipo=db.Column(db.String(15),nullable=False) #Tipo de EVENTO
    aprobado = db.Column(db.Boolean, nullable=False, default=False)
   # estado=db.Column(db.Boolean,nullable=False)
    #Relaciones entre evento y comentario (Uno a muchos) (En caso de eliminar un evento , con cascade eliminamos todos los comentarios que estaban asociados a ese evento):
    comentarios = db.relationship("Comentario", back_populates="evento",cascade="all, delete-orphan") #back_populates establece que existe una relacion con el atributo evento de la clase Comentario
    #Relacion entre usuario y evento (Uno a Muchos):
    usuarioId = db.Column(db.Integer, db.ForeignKey('usuario.usuarioId'), nullable=False)
    usuario = db.relationship('Usuario',back_populates="eventos") #back_populates establece que existe una relacion con el atributo eventos de la clase Usuario

    #Funcion que determina que se mostrará si se imprime el objeto
    def __repr__(self):
        return '<Evento: %r %r %r %r %r %r Usuario: %r>' % (self.nombre, self.fecha,self.hora, self.descripcion,self.imagen,self.tipo,self.usuarioId) #imprime el objeto

    #Convertimos objeto de tipo Evento a JSON
    def a_json(self):
        #Creamos un diccionario (clave-valor) para formar el estilo de un archivo JSON
        evento_json={
            'eventoId':url_for('apiGetEventoById',id=self.eventoId, _external=True), #Obtenemos la url de evento perteneciente a un id X
            'nombre':self.nombre,
            'fecha':self.fecha,
            'hora':str(self.hora),
            'descripcion':self.descripcion,
            'imagen':self.imagen,
            'tipo':self.tipo,
            'aprobado':self.aprobado
        }
        return evento_json

    #Metodo que usaremos sin necesidad de instanciar la clase.
    @staticmethod
    # Convertir JSON a objeto
    def desde_json(evento_json):
        nombre = evento_json.get('nombre')
        fecha = evento_json.get('fecha')
        hora = evento_json.get('hora')
        descripcion=evento_json.get('descripcion')
        imagen=evento_json.get('imagen')
        tipo=evento_json.get('tipo')
        return Evento(nombre=nombre, fecha=fecha,hora=hora,descripcion=descripcion,imagen=imagen,tipo=tipo)

#Definimos todos los campos y relaciones de la tabla usuario de la BD
class Usuario(UserMixin,db.Model):
    usuarioId=db.Column(db.Integer,primary_key=True)
    nombre=db.Column(db.String(20),nullable=False)
    apellido=db.Column(db.String(20),nullable=False)
    email=db.Column(db.String(30),nullable=False,unique=True, index=True)
    password=db.Column(db.String(128),nullable=False)
    admin=db.Column(db.Boolean,nullable=False)

    #Relacion entre evento y usuario (Relacion Uno-Muchos):
    eventos = db.relationship("Evento", back_populates="usuario", cascade="all, delete-orphan") #back_populates establece que existe una relacion con el atributo usuario de la clase Evento

    # Relacion entre usuario y comentario (Relacion Uno-Muchos):
    comentarios = db.relationship("Comentario", back_populates="usuario", cascade="all, delete-orphan") #back_populates establece que existe una relacion con el atributo usuario de la clase Comentario


    # PASSWRD es la contraseña no cifrada.
    #password es la contraseña cifrada.
    # No permitir leer la pass de un usuario
    @property
    def passwrd(self):  # no puedo acceder directamente al atributo contraseña
        raise AttributeError('La password no puede leerse')

    # Al setear la pass generar un hash
    @passwrd.setter
    def passwrd(self, passwrd):
        self.password = generate_password_hash(passwrd)

    # Al verificar pass comparar hash del valor ingresado con el de la db
    def check_password(self, passwrd):
        return check_password_hash(self.password,passwrd)

    def get_id(self):
        return (self.usuarioId)
    def is_admin(self): #Comprobamos si el usuario logueado es admin.
        aux=False
        if self.admin==1:
            aux=True
        return aux

#Funcion que determina que se mostrará si se imprime el objeto
    def __repr__(self):
        return '<Usuario: %r %r %r %r %r>' % (self.nombre, self.apellido, self.email,self.password,self.admin) #imprime el objeto


@login_manager.user_loader
def load_user(user_id): #Indica como obtener el usuario de la BD a partir del ID guardado en la sesion
    return Usuario.query.get(int(user_id)) #especificamos que el usuario se obtiene por id.

#Defino todos los campos, sus parametros y relaciones de la tabla comentario.
class Comentario(db.Model):
    comentarioId=db.Column(db.Integer,primary_key=True)
    contenido=db.Column(db.String(500),nullable=False)
    fechahora=db.Column(db.DateTime,nullable=False)

    #Relacion entre evento y comentario
    eventoId = db.Column(db.Integer, db.ForeignKey('evento.eventoId'), nullable=False)
    evento = db.relationship('Evento',back_populates="comentarios") #back_populates establece que existe una relacion con el atributo comentarios de la clase Evento

    #Relacion entre usuario y comentario:
    usuarioId = db.Column(db.Integer, db.ForeignKey('usuario.usuarioId'), nullable=False)
    usuario = db.relationship('Usuario', back_populates="comentarios") #back_populates establece que existe una relacion con el atributo comentarios de la clase Usuario


    #Convertimos objeto de tipo Comentario a JSON
    def a_json(self):
        comentario_json={
            'comentarioId':url_for('apiGetComentarioById',id=self.comentarioId, _external=True), #Obtenemos la url de comentario
            'contenido':self.contenido,
            'fechahora':self.fechahora,
        }
        return comentario_json
    #Funcion que determina que se mostrará si se imprime el objeto
    def __repr__(self):
        return '<Comentario: %r %r Evento: %r Usuario: %r>' % (self.texto, self.fechahora,self.eventoId,self.usuarioId) #imprime el objeto

#db.drop_all() #Elimina las tablas de la BD. Si ejecuto este archivo python borra las tablas y vuelve a crearlas apartir del modelo
db.create_all() #Crea las tablas de la db a patir de los modelos
