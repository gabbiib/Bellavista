from django.shortcuts import render, redirect
from .models import Usuarios_gestion, Rol_gestion, Problemas, Marcos
from django.contrib import messages


def gestion_usuario(request):
    UsuariosListados = Usuarios_gestion.objects.all()
    return render(request, "gestionUsuarios.html", {"usuarios": UsuariosListados})

def edicionUsuario(request, rut):
    usuario = Usuarios_gestion.objects.get(rut=rut)
    
    if request.method == 'POST':
        # Aquí se pueden recoger y actualizar los datos del usuario
        usuario.nombre = request.POST['txtNombre']
        usuario.apellido_p = request.POST['txtApellido_P']
        usuario.apellido_m = request.POST['txtApellido_M']
        usuario.fecha_n = request.POST['txtFecha_n']
        usuario.correo = request.POST['numCorreo']
        usuario.telefono = request.POST['numTelefono']
        usuario.save()  # Guardar cambios en la base de datos
        return redirect('/data/gestion_usuario/')  # Cambia esto por la ruta que quieras

    return render(request, "edicionUsuario.html", {"usuario": usuario})

def registrarUsuario(request):
    if request.method == "POST":
        rut = request.POST['txtRut']
        nombre = request.POST['txtNombre']
        apellido_p = request.POST['txtApellido_P']
        apellido_m = request.POST['txtApellido_M']
        fecha_n = request.POST['txtFecha_n']
        correo = request.POST['numCorreo']
        telefono = request.POST['numTelefono']
        password = request.POST['numPassword']

        # Obtener el rol a partir del valor recibido en el formulario
        rol_id = request.POST['txtRol']  # Recibe el ID del rol del formulario
        try:
            rol_instance = Rol_gestion.objects.get(id_rol=rol_id) 
        except Rol_gestion.DoesNotExist:
            messages.error(request, 'Error: El rol seleccionado no existe.')
            return redirect('/data/gestion_usuario/')  # Redirigir a la página de datos en caso de error

        # Crear el usuario asignando la instancia del rol
        usuario = Usuarios_gestion.objects.create(
            rut=rut,
            nombre=nombre,
            apellido_p=apellido_p,
            apellido_m=apellido_m,
            fecha_n=fecha_n,
            rol=rol_instance,  # Asignar la instancia del rol
            correo=correo,
            telefono=telefono,
            password=password
        )

        messages.success(request, '¡Usuario registrado!')
        return redirect('/data/gestion_usuario/')  # Cambia esta línea para redirigir a la página deseada
    else:
        return redirect('/data/gestion_usuario/')  # También redirige aquí si no es un POST


def eliminarUsuario(request, rut):
    usuario = Usuarios_gestion.objects.get(rut=rut)
    usuario.delete()

    messages.success(request, '¡Usuario eliminado!')

    return redirect('/data/gestion_usuario/')

##-----------------------PROBLEMAS-----------------------------

def gestion_problema(request):
    ProblemasListados = Problemas.objects.all()
    return render(request, "gestionProblemas.html", {"problemas": ProblemasListados})

def edicionProblema(request, id):
    problema = Problemas.objects.get(id=id)
    
    if request.method == 'POST':
        problema.nombre = request.POST['txtProblema']
        problema.descripcion = request.POST['txtDescripcion']
        problema.save()
        return redirect('/data/gestion_problema/')  

    return render(request, "edicionProblema.html", {"problema": problema})

def registrarProblema(request):
    if request.method == "POST":
        problema = request.POST['txtProblema']
        descripcion = request.POST['txtDescripcion']
       
        nuevo_problema = Problemas.objects.create(
            nombre=problema,
            descripcion=descripcion,
        )

        messages.success(request, '¡Problema registrado!')
        return redirect('/data/gestion_problema/') 
    else:
        return redirect('/data/gestion_problema/')  


def eliminarProblema(request, id):
    problema = Problemas.objects.get(id=id)
    problema.delete()

    messages.success(request, '¡Problema eliminado!')

    return redirect('/data/gestion_problema/')

##-----------------------MARCOS-----------------------------


def gestion_marcos(request):
    MarcosListados = Marcos.objects.all()
    return render(request, "gestionMarco.html", {"marcos": MarcosListados})

def edicionMarco(request, id):
    marco = Marcos.objects.get(id=id)
    
    if request.method == 'POST':
        marco.nombre = request.POST['txtMarco']
        marco.descripcion = request.POST['txtDescripcion']
        marco.save()
        return redirect('/data/gestion_marco/')  

    return render(request, "edicionMarco.html", {"marco": marco})

def registrarMarco(request):
    if request.method == "POST":
        marco = request.POST['txtMarco']
        descripcion = request.POST['txtDescripcion']
       
        nuevo_marco = Marcos.objects.create(
            nombre=marco,
            descripcion=descripcion,
        )

        messages.success(request, '¡Marco registrado!')
        return redirect('/data/gestion_marco/') 
    else:
        return redirect('/data/gestion_marco/')  


def eliminarMarco(request, id):
    marco = Marcos.objects.get(id=id)
    marco.delete()

    messages.success(request, '¡Marco eliminado!')

    return redirect('/data/gestion_marco/')