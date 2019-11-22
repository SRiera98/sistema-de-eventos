import time, smtplib
from run import app,mail
from flask_mail import Mail, Message #Importar para enviar Mail
from threading import Thread #Importar hilos
from flask import render_template,redirect, url_for
from flask import Flask
from errores import logger
#-------------------Comienzo Funciones Email------------------------------------------------------------------------

#Función para mandar un mail de manera asincrónica
def enviarMailAsincronico(app, msg):

    #Se utiliza el contexto de la aplicación para tener acceso a la configuración
    with app.app_context():
        try:
            #Enviar mail
            mail.send(msg)
            print("Mail enviado correctamente")

        #Mostrar errores por consola.
        #Enviamos el error sucedido (dependiendo a que except entre) a la funcion logger parseandolo
        # a string junto con la ubicacion del error hardcodeada, y ademas imprimiendo el error por la consola.
        except smtplib.SMTPAuthenticationError as e:
            print("Error de autenticación, MAIL_USER o MAIL_PASSWORD incorrectos \n"+str(e))
            logger(str(e),"enviarMailAsincronico in funciones_mail.py")
        except smtplib.SMTPServerDisconnected as e:
            print("Servidor desconectado: \n\n\n"+str(e))
            logger(str(e), "enviarMailAsincronico in funciones_mail.py")
        except smtplib.SMTPSenderRefused as e:
            print("Se requiere autenticación: "+str(e))
            logger(str(e), "enviarMailAsincronico in funciones_mail.py")
        except smtplib.SMTPException as e: #Error generico
            print("Error: "+str(e))
            logger(str(e), "enviarMailAsincronico in funciones_mail.py")
        except OSError as e: #Excepcion generica para errores de entrada/salida para capturar el error del puerto bloqueado.
            logger(str(e), "enviarMailAsincronico in funciones_mail.py")

#Función que genera el hilo que enviará el mail
def enviarMailThread(to, subject, template, **kwargs):
    #Realizamos la configuraciones del mail respecto al html que vamos a enviar:

    #Configurar asunto, emisor y destinatarios
    msg = Message( subject, sender=app.config['FLASKY_MAIL_SENDER'], recipients=[to])
    #Seleccionar template para mensaje de texto plano
    msg.body = render_template(template + '.txt', **kwargs)
    #Seleccionar template para mensaje HTML
    msg.html = render_template(template + '.html', **kwargs)

    #Crear hilo
    thr = Thread(target=enviarMailAsincronico, args=[app, msg])
    #Iniciar hilo
    thr.start()