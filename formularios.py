from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField,validators,TextField,SelectField
from wtforms.fields.html5 import EmailField,DateField,DateTimeField
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms_components import TimeField
from wtforms.validators import ValidationError
from modelos import *
class FormularioRegistro(FlaskForm):

    #Función de validación de nombre de usuario. Esta funcion recibe dos argumentos , form que es el formulario, en este caso FormularioRegistro,
    # y field que es el campo del formulario donde estamos aplicando el verificador, en este caso el nombre de usuario
    def nombre_usuario(form,field):
        #Verificar que no contenga guiones bajos o numeral
        if (field.data.find("_")!= -1) or (field.data.find("#")!= -1) :
            #Mostrar error de validación
             raise validators.ValidationError("El nombre de usuario solo puede contener letras, números y puntos.")

    nombre=StringField('Nombre',[validators.DataRequired(),validators.length(min=3,max=30,message='Ingrese un nombre valido'),nombre_usuario])
    apellido=StringField('Apellido',[validators.DataRequired()])
    email=EmailField('Correo Electronico',[validators.DataRequired(),validators.email(message='Ingrese un mail valido')])
    contrasena=PasswordField('Contraseña',[validators.DataRequired(),validators.EqualTo('verificar',message='La contraseña no coincide')]) #EqualTo recibe la variable con la que tiene que comparar la coincidencia,
                                                                                                                                           # y un mensaje indicando el posible error si la coincidencia no ocurre.
    verificar = PasswordField('Verificar Contraseña')
    registro=SubmitField('Registrarse')
    #Verificar si el email ya existe en la db
    def validate_email(self, field):
        #Si obtenemos resultados en la consulta, es por que el mail ya esta registrado.
        if Usuario.query.filter_by(email=field.data).first():
            raise ValidationError('El email ya ha sido registrado.')

#Definimos la clase para luego instanciar y utilizar el formulario de inicio de sesion.
class FormularioLogin(FlaskForm):
    email = StringField('Correo Electronico', [validators.DataRequired()])
    contrasena=PasswordField('Contraseña',[validators.DataRequired()])
    iniciar=SubmitField('Iniciar Sesión')
    registro=SubmitField('Registrarse')

#FDefinimos la clase para un formulario de nuevo evento.
class FormularioCrearEvento(FlaskForm):

    #Función para hacer un campo opcional
    def opcional(field):
        field.validators.insert(0, validators.Optional())

    titulo=StringField('Título Evento',[validators.DataRequired()])
    fecha=DateField('Fecha Evento',[validators.DataRequired(message="Ingrese una fecha válida")])
    hora = TimeField('Hora Evento',[validators.DataRequired(message="Ingrese una hora válida")])
    tipo=[
        (None,'--Ingrese tipo de Evento--'),
        ('Fiesta','Fiesta'),
        ('Conferencia','Conferencia'),
        ('Carreras','Carreras'),
        ('Festival','Festival'),
        ('Curso','Curso'),
        ('Obra','Obra')
    ]
    opciones=SelectField('Tipo de Evento',choices=tipo)
    descripcion=StringField('Descripcion Evento',[validators.required(message='Ingrese breve descripcion')])
    imagen = FileField('Imagen Evento',validators=[ validators.DataRequired(), FileAllowed(['jpg', 'png'], 'El archivo debe ser una imagen jpg o png')])
    envio_evento=SubmitField('Enviar Evento')

#Formulario para realizar comentarios en los eventos.
class FormularioComentario(FlaskForm):
    comentario=StringField('Escribir un Comentario:',[validators.DataRequired(message="Comentario faltante")])
    submit=SubmitField("Enviar Comentario")

#Formulario para filtrar eventos.
class FormularioFiltrarEvento(FlaskForm):
    desde_fecha=DateField('Desde',[validators.Optional()])
    hasta_fecha=DateField('Hasta',[validators.Optional()])
    opciones=[
        ('null','--Ingrese tipo de Evento--'),
        ('Fiesta','Fiesta'),
        ('Conferencia','Conferencia'),
        ('Carreras','Carreras'),
        ('Festival','Festival'),
        ('Curso','Curso'),
        ('Obra','Obra')
    ]
    categoria=SelectField('Tipo de Evento',choices=opciones)
    envio_filtrar=SubmitField('Buscar')

