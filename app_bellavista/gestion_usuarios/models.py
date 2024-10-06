from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _

class trabajadores(models.Model):
    id_trabajador = models.AutoField(max_length=8, primary_key=True)
    Nombre = models.CharField(max_length=25)
    Apellido_P = models.CharField(max_length=15)
    Apellido_M = models.CharField(max_length=15)
    Fecha_N = models.DateField()
    cod_rol = models.IntegerField(1)
    correo = models.EmailField()
    password = models.CharField(max_length=255, null=True)

    def set_password(self, raw_password):
        """Hashea la contraseña antes de guardarla"""
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        """Verifica si la contraseña es correcta"""
        return check_password(raw_password, self.password)

    class Meta:
        db_table = 'trabajadores'  # Nombre de la tabla en la base de datos
    
    def __str__(self):
        return f'{self.Nombre} {self.Apellido_P} {self.Apellido_M}'
    def full_name(self):
        return f"{self.Nombre} {self.Apellido_P} {self.Apellido_M}"

class Rol(models.Model):
    id_rol = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()

class reportes_problemas(models.Model):
    rut_usuario = models.ForeignKey(trabajadores, on_delete=models.CASCADE)
    tipo_incidente = models.CharField(max_length=100)
    descripcion = models.TextField()
    marco = models.CharField(max_length=255, blank=True, null=True) 
    medida_marco = models.TextField(default='Sin medir')
    foto_url = models.ImageField(upload_to='reportes_fotos/', blank=True, null=True)  # Cambiado a ImageField
    fecha_reporte = models.DateField(null=True)

    def __str__(self):
        return self.tipo_incidente

class gestion_fallas(models.Model):
    id_reporte = models.ForeignKey(reportes_problemas, on_delete=models.CASCADE)
    rut_usuario = models.ForeignKey(trabajadores, on_delete=models.CASCADE)
    descripcion = models.TextField()
    ubicacion_geografica = models.CharField(max_length=255)
    estado = models.CharField(max_length=50)
    fecha_reporte = models.DateTimeField()
    latitud = models.FloatField(null=True, blank=True)  # Permite null en la base de datos y blank en formularios
    longitud = models.FloatField(null=True, blank=True)