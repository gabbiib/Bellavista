from django import forms
from .models import Reportes_Problemas

class RecuperarContrasenaForm(forms.Form):
    email = forms.EmailField(label='Correo Electrónico', widget=forms.EmailInput(attrs={'placeholder': 'Ingresa tu correo electrónico'}))

class ContactarAdminForm(forms.Form):
    email = forms.EmailField(label='Correo Electrónico', widget=forms.EmailInput(attrs={'placeholder': 'Ingresa tu correo electrónico'}))
    mensaje = forms.CharField(label='Mensaje', widget=forms.Textarea(attrs={'placeholder': 'Escribe tu mensaje aquí...'}))


class ReporteForm(forms.ModelForm):
    class Meta:
        model = Reportes_Problemas
        fields = ['descripcion', 'marco', 'medida_marco']