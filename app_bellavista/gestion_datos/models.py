from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group, Permission
from datetime import datetime

class Rol_gestion(models.Model):
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

class Usuarios_gestion(AbstractBaseUser, PermissionsMixin):
    rut = models.CharField(max_length=9, primary_key=True)
    nombre = models.CharField(max_length=100)
    apellido_p = models.CharField(max_length=100)
    apellido_m = models.CharField(max_length=100)
    fecha_n = models.DateField()
    rol = models.ForeignKey(Rol_gestion, on_delete=models.CASCADE, db_column='id_rol')
    correo = models.EmailField(max_length=150, unique=True, null=True, blank=True)  # Opcional para trabajadores
    telefono = models.CharField(max_length=15)    
    password = models.CharField(max_length=255)
    codigo_recuperacion = models.CharField(max_length=6, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

# Añade related_name para evitar conflicto con auth.User
    groups = models.ManyToManyField(
        Group,
        related_name='usuarios_gestion_groups',  # Cambia related_name para evitar conflictos
        blank=True
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='usuarios_gestion_permissions',  # Cambia related_name para evitar conflictos
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

class Problemas(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(max_length=100)

class Marcos(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=40)
    descripcion = models.TextField(max_length=100)

# Create your models here.
