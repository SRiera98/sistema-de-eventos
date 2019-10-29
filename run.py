from flask import Flask
import os
from flask_sqlalchemy import SQLAlchemy #Incluye sqlAlchemy
from dotenv import load_dotenv #carga las variables de entorno
from flask_mail import Mail
from flask_login import LoginManager #modulo para manejar el login de usuarios
from flask_wtf import CSRFProtect #importar para proteccion CSRF
app=Flask(__name__)
load_dotenv()


#Configuraciones de mail
app.config['SECRET_KEY'] =os.getenv('SECRET_KEY')
#Ip del host de salida
app.config['MAIL_HOSTNAME'] = 'localhost'
#Dirección del servidor mail utilizado
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
#Puerto del servidor mail saliente SMTP
app.config['MAIL_PORT'] = 587
#Especificar conexión con SSL/TLS
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['FLASKY_MAIL_SENDER'] = 'EventFlare Eventos <evenflare@eventos.com>'

#Sincronizacion con BD
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True   #Sigue las modificaciones en tiempo real
#Configuración de conexion de base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://'+os.getenv('DB_USERNAME')+':'+os.getenv('DB_PASS')+'@localhost/bdproyecto'  #Formato de coneccion,simple es el nombre de usuario.

#Inicializar mail
mail = Mail(app)
#Instancia que representa la base de datos
db = SQLAlchemy(app)
#establecemos el login
login_manager = LoginManager(app)

csrf = CSRFProtect(app) #Iniciar protección CSRF
# -*- coding: utf-8 *-*


if __name__ == '__main__':
    from rutas import *
    from rutas_api import *
    app.run(port = 8000,debug=True)