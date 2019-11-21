
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