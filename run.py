from flask import Flask
import os
from flask_sqlalchemy import SQLAlchemy #Incluye sqlAlchemy
from dotenv import load_dotenv #carga las variables de entorno
from flask_mail import Mail
from flask_login import LoginManager #modulo para manejar el login de usuarios
from flask_wtf import CSRFProtect #importar para proteccion CSRF
app=Flask(__name__) #Instanciamos el microframework Flask
load_dotenv() #Cargamos las variables de nuestro entorno.

#Sincronizacion con BD
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True   #Sigue las modificaciones que realicemos en tiempo real
#Configuración de conexion de base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://'+os.getenv('DB_USERNAME')+':'+os.getenv('DB_PASS')+'@localhost/bdproyecto'  #Formato de coneccion a la BD.

#Configuraciones de mail
app.config['SECRET_KEY'] =os.getenv('SECRET_KEY') #Trae la clave secreta del entorno, para que ninguna api de terceros se haga pasar por nosotros. Esta clave secreta se comprueba en varios lugares por el motivo antes mencionado


app.config['MAIL_HOSTNAME'] = 'localhost' #Ip del host de salida
app.config['MAIL_SERVER'] = 'smtp.gmail.com' #Dirección del servidor mail utilizado
app.config['MAIL_PORT'] = 587  #Puerto del servidor mail saliente SMTP
app.config['MAIL_USE_TLS'] = True #Especificar conexión con SSL/TLS, diferentes tipos de protocolos para las seguridad con el servidor
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME') #Configura el mail con el que enviaremos los mails a nuestros usuarios, dicho mail esta almacenado como variable de entorno por temas de seguridad.
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD') #Configuramos la password del mail nuestro con el que estamos enviando correos, almacenada como variable de entorno
app.config['FLASKY_MAIL_SENDER'] = 'EventFlare Eventos <evenflare@eventos.com>' #Configuramos un alias con el cual el usuario recibira el mail, pero no representa el mail real.


#Inicializamos mail pasandole la instancia de Flask
mail = Mail(app)
#Instancia que representa la base de datos
db = SQLAlchemy(app)
#establecemos un instancia de objeto de tipo LoginManager, para manejar sesiones en nuestra pagina web.
login_manager = LoginManager(app)

csrf = CSRFProtect(app) #Iniciamos la protección CSRF. Es util usar un token CSRF, permite que nuestra aplicación haga las peticiones desde nuestro sitio, lo que hacemos es instanciar el CSRF
# -*- coding: utf-8 *-*


if __name__ == '__main__': #Nos aseguramos que solo se ejecute el servidor cuando ejecutemos nuestro archivo .py, configurando para que Flask arranque en el puerto 8000.
    from rutas import *
    from rutas_api import *
    from errores import  *
    app.run(port = 8000,debug=True)