from run import db
from modelos import *
def listar_eventos():
    import csv
    with open('actividades-culturales.csv',encoding="UTF-8") as f:
        a = [{k: v for k, v in row.items()}
            for row in csv.DictReader(f, skipinitialspace=True)]
    return a
def listar_comentarios():
    import csv
    with open('comentarios.csv',encoding="UTF-8") as f:
        a = [{k: v for k, v in row.items()}
            for row in csv.DictReader(f, skipinitialspace=True)]
    return a
def listar_eventos_bd():
    lista_eventos=db.session.query(Evento).all()
    return lista_eventos
def listar_comentarios_bd():
    lista_comentarios = db.session.query(Comentario).all()
    return lista_comentarios