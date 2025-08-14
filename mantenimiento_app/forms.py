from django.contrib.auth.models import User
from .models import OrdenAlistamiento, Vehiculo
from django import forms

class CrearOrdenForm(forms.ModelForm):
    class Meta:
        model = OrdenAlistamiento
        fields = [
            'vehiculo',
            'user',
        ]

        labels = {
            'user': 'Tecnico'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user'].queryset = User.objects.filter(groups__name='Tecnicos_mtto')


class CsvUploadForm(forms.Form):
    archivo_csv = forms.FileField()


class CrearVehiculoForm(forms.ModelForm):
    class Meta:
        model = Vehiculo
        fields = '__all__'
        
        labels = {
            'vehiculo_id': 'Vehiculo'
        }

    

