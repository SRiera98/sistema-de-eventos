#En estas 5 funciones lo unico que hacemos es enviar en cada una de ellas un objeto de tipo formulario y luego se
#imprime en consola cada uno de los atributos de ese objeto de tipo formulario accediendo a los mismos,
# es un formulario en particular.
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