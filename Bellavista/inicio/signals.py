from django.db.models.signals import post_save
from django.dispatch import receiver
from gestion_reportes.models import Asignacion
from twilio.rest import Client
from django.conf import settings

@receiver(post_save, sender=Asignacion)
def enviar_notificacion_tarea(sender, instance, created, **kwargs):
    if created:
        usuario = instance.trabajador  # Corregido a 'trabajador'
        mensaje = (
            f"Hola {usuario.nombre}, se te ha asignado una nueva tarea:\n\n"
            f"Descripción: {instance.tarea.descripcion}\n"  # Accede a los atributos de 'tarea'
            f"Prioridad: {instance.tarea.prioridad}\n"
            f"Por favor, revisa tu panel de tareas."
        )

        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        client.messages.create(
            body=mensaje,
            from_= settings.TWILIO_PHONE_NUMBER,
            to= usuario.telefono
        )