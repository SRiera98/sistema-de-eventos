#Creacion de Tablas de BD
Proyecto de Santiago Riera.
Para crear las tablas realizamos:
python3
>>>import modelos
>>>import db
>>>db.create_all()

Recomendable si queremos vaciar las tablas y volver a crearlas ejecutar:
>>>db.drop_all()
