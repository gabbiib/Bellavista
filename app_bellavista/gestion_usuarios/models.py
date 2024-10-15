from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group, Permission
from datetime import datetime

# ----------------------------- GESTION DE ROLES -----------------------------
### okey 
class Rol(models.Model):
    id_rol = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()

    def _str_(self):
        return self.nombre


# ----------------------------- USUARIOS ---------------------------------
class UsuariosManager(BaseUserManager):
    def create_user(self, rut, password=None, **extra_fields):
        if not rut:
            raise ValueError(_('El RUT debe ser proporcionado'))
        user = self.model(rut=rut, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, rut, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(rut, password, **extra_fields)

class Usuarios(AbstractBaseUser, PermissionsMixin):
    rut = models.CharField(max_length=9, primary_key=True)
    nombre = models.CharField(max_length=100)
    apellido_p = models.CharField(max_length=100)
    apellido_m = models.CharField(max_length=100)
    fecha_n = models.DateField()
    rol = models.ForeignKey(Rol, on_delete=models.CASCADE, db_column='id_rol')
    correo = models.EmailField(max_length=150, unique=True, null=True, blank=True)  # Opcional para trabajadores
    telefono = models.CharField(max_length=15)    
    password = models.CharField(max_length=255)
    codigo_recuperacion = models.CharField(max_length=6, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

# Añade related_name para evitar conflicto con auth.User
    groups = models.ManyToManyField(
        Group,
        related_name='usuarios_groups',  # Cambia related_name para evitar conflictos
        blank=True
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='usuarios_permissions',  # Cambia related_name para evitar conflictos
        blank=True
    )

    objects = UsuariosManager()

    USERNAME_FIELD = 'rut'
    REQUIRED_FIELDS = ['telefono']  

    def __str__(self):
        return str(self.rut)

    def __str__(self):
        return f'{self.nombre} {self.apellido_p} {self.apellido_m}'

    def full_name(self):
        return f"{self.nombre} {self.apellido_p} {self.apellido_m}"
    
# ----------------------------- HISTORIAL DE CAMBIOS -----------------------------
class Historial_De_Cambios(models.Model):
    rut = models.ForeignKey(Usuarios, on_delete=models.CASCADE)
    tipo_cambio = models.CharField(max_length=100)
    fecha = models.DateField()


# ----------------------------- GESTION DE PROBLEMAS -----------------------------
class Reportes_Problemas(models.Model):
    rut_usuario = models.ForeignKey(Usuarios, on_delete=models.CASCADE)
    tipo_incidente = models.CharField(max_length=100)
    descripcion = models.TextField()
    marco = models.CharField(max_length=255, blank=True, null=True) 
    medida_marco = models.TextField(default='Sin medir')
    foto_url = models.ImageField(upload_to='reportes_fotos/', blank=True, null=True)
    fecha_reporte = models.DateTimeField(auto_now_add=True)
    latitud = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitud = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)

    def __str__(self):
        return self.tipo_incidente

    
class Gestion_Fallas(models.Model):
    id_reporte = models.ForeignKey(Reportes_Problemas, on_delete=models.CASCADE)
    rut_usuario = models.ForeignKey(Usuarios, on_delete=models.CASCADE)
    descripcion = models.TextField()
    ubicacion_geografica = models.CharField(max_length=255)
    estado = models.CharField(max_length=50)
    fecha_reporte = models.DateTimeField()

# ----------------------------- GESTION DE TAREAS -----------------------------

class Tareas(models.Model):
    ESTADOS_TAREA = [
        ('en_espera', 'En Espera'),
        ('en_progreso', 'En Progreso'),
        ('terminada', 'Terminada'),
    ]   
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    prioridad = models.CharField(max_length=20, choices=[('Alta', 'Alta'), ('Media', 'Media'), ('Baja', 'Baja')])



class Asignacion(models.Model):
    tarea = models.ForeignKey(Tareas, on_delete=models.CASCADE)
    trabajador = models.ForeignKey(Usuarios, on_delete=models.CASCADE, limit_choices_to={'rol__nombre': 'Trabajador'})
    estado = models.CharField(max_length=20, default='En espera', choices=[('En espera', 'En espera'), ('En progreso', 'En progreso'), ('Completada', 'Completada')])
    asignado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    fecha_fin = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.estado == 'terminada' and not self.fecha_fin:
            self.fecha_fin = timezone.now() 
        super().save(*args, **kwargs)