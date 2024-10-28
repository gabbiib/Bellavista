from django import forms
from .models import Reportes_Problemas


class ReporteForm(forms.ModelForm):
    class Meta:
        model = Reportes_Problemas
        fields = ['descripcion', 'marco', 'medida_marco']