from django.shortcuts import render, redirect, get_object_or_404
from .models import Usuarios, Rol, Problemas, Marcos
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.shortcuts import redirect

def gestion_usuario(request):
    UsuariosListados = Usuarios.objects.all()
    return render(request, "gestionUsuarios.html", {"usuarios": UsuariosListados})

def registrarUsuario(request):
    if request.method == "POST":
        rut = request.POST['txtRut']
        nombre = request.POST['txtNombre']
        apellido_p = request.POST['txtApellido_P']
        apellido_m = request.POST['txtApellido_M']
        fecha_n = request.POST['txtFecha_n']
        correo = request.POST['numCorreo']
        telefono = '+569' + request.POST['numTelefono']
        password = request.POST['numPassword']
        
       
        rol_id = request.POST['txtRol']
        try:
            rol_instance = Rol.objects.get(id_rol=rol_id) 
        except Rol.DoesNotExist:
            messages.error(request, 'Error: El rol seleccionado no existe.')
            return redirect('/data/gestion_usuario/')

  
        usuario = Usuarios.objects.create(
            rut=rut,
            nombre=nombre,
            apellido_p=apellido_p,
            apellido_m=apellido_m,
            fecha_n=fecha_n,
            rol=rol_instance,
            correo=correo,
            telefono=telefono,
            password=make_password(password) 
        )

        messages.success(request, '¡Usuario registrado!')
        return redirect('/data/gestion_usuario/')
    else:
        return redirect('/data/gestion_usuario/')
    
def edicionUsuario(request, rut):
    usuario = Usuarios.objects.get(rut=rut)
    
    if request.method == 'POST':
        cambios = False 
        
        if (request.POST['txtNombre'] != usuario.nombre or
            request.POST['txtApellido_P'] != usuario.apellido_p or
            request.POST['txtApellido_M'] != usuario.apellido_m or
            request.POST['txtFecha_n'] != str(usuario.fecha_n) or
            request.POST['numCorreo'] != usuario.correo or
            request.POST['numTelefono'] != usuario.telefono):
            cambios = True
        
        nueva_contraseña = request.POST.get('numPassword', '').strip()
        if nueva_contraseña:  
            cambios = True 
            usuario.password = make_password(nueva_contraseña)

        if not cambios:
            messages.error(request, 'Debe realizar cambios en alguno de los campos para guardar.')
            return redirect(f'/data/gestion_usuario/')
        
        usuario.nombre = request.POST['txtNombre']
        usuario.apellido_p = request.POST['txtApellido_P']
        usuario.apellido_m = request.POST['txtApellido_M']
        usuario.fecha_n = request.POST['txtFecha_n']
        usuario.correo = request.POST['numCorreo']
        
        telefono = request.POST['numTelefono']
        if not telefono.startswith('+569'):
            telefono = '+569' + telefono
        usuario.telefono = telefono
        
        usuario.save()
        
        messages.success(request, 'Usuario actualizado correctamente.')
        return redirect('/data/gestion_usuario/')
    
    return render(request, "gestionUsuarios.html")
                  
def eliminarUsuario(request, rut):
    usuario = get_object_or_404(Usuarios, rut=rut)
    usuario.delete()
    messages.success(request, '¡Usuario eliminado exitosamente!')
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