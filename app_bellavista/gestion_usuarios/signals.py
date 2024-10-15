from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Tareas, Usuarios
from twilio.rest import Client
from django.conf import settings

@receiver(post_save, sender=Tareas)
def enviar_notificacion_tarea(sender, instance, created, **kwargs):
    if created:
        usuario = instance.rut_usuario
        mensaje = f"Hola {usuario.nombre}, se te ha asignado una nueva tarea:\n\n" \
                  f"Descripción: {instance.descripcion}\n" \
                  f"Prioridad: {instance.prioridad}\n" \
                  f"Por favor, revisa tu panel de tareas."

        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        client.messages.create(
            body=mensaje,
            from_='whatsapp:' + settings.TWILIO_PHONE_NUMBER,
            to='whatsapp:' + usuario.telefono 
        )
