# forms.py
from django import forms
from gestion_datos.models import Marcos  # Asegúrate de importar el modelo Marcos
from .models import Reportes_Problemas

class ReporteForm(forms.ModelForm):
    marco = forms.ModelChoiceField(
        queryset=Marcos.objects.all(),  # Aquí seleccionamos todos los marcos
        empty_label="Seleccione un marco",  # Texto que aparece cuando no hay selección
        widget=forms.Select(attrs={'class': 'form-control'})  # Estilo 'form-control' para el <select>
    )

    class Meta:
        model = Reportes_Problemas
        fields = ['descripcion', 'marco', 'medida_marco']
