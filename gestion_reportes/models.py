from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from gestion_datos.models import Usuarios


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
    estado = models.CharField(max_length=50)
    fecha_reporte = models.DateTimeField()
    fecha_solucion = models.DateTimeField()

#class Gestion_Fallas(models.Model):
#    id_reporte = models.ForeignKey(Reportes_Problemas, on_delete=models.CASCADE)
#    rut_usuario = models.ForeignKey(Usuarios, on_delete=models.CASCADE)
#    descripcion = models.TextField()
#    ubicacion_geografica = models.CharField(max_length=255)
#    estado = models.CharField(max_length=50)
#    fecha_reporte = models.DateTimeField()


# ----------------------------- GESTION DE TAREAS -----------------------------

class Tareas(models.Model):
    ESTADOS_TAREA = [
        ('En espera', 'En Espera'),
        ('En progreso', 'En Progreso'),
        ('Completada', 'Completada'),
    ]   
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    prioridad = models.CharField(max_length=20, choices=[('Alta', 'Alta'), ('Media', 'Media'), ('Baja', 'Baja')])
    creado_en = models.DateTimeField(auto_now_add=True)
    id_reporte = models.ForeignKey(Reportes_Problemas, on_delete=models.SET_NULL, null=True, blank=True)
    es_predeterminado = models.BooleanField(default=False)



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