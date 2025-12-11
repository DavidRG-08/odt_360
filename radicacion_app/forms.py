from django.contrib.auth.models import User
from .models import *
from django import forms


class CrearRadicadoRecibidosForm(forms.ModelForm):
    class Meta:
        model = RadicacionRecibidos
        exclude = ['radicador', 'fecha_radicacion', 'id']
        fields = '__all__'
        labels = {
            #'id': 'Número de Radicado',
            'medio_ingreso': 'Medio de ingreso',
            'tipo_comunicacion': 'Tipo de Comunicación',
            'tipo_documento': 'Tipo de Documento',
            'num_rad_llegada': 'Número de Radicado de Llegada', 
            'responsable_por_responder': 'Responsable Asignado',
            'requiere_respuesta': 'Requiere Respuesta',
            'tiempo_respuesta': 'Tiempo para Respuesta (días)',
            'fecha_maxima_respuesta': 'Fecha Máxima de Respuesta',
            'respuesta_rad_interno': 'Respuesta al Radicado Interno',
            'estado_respuesta': 'Estado de la Respuesta',
            'fecha_respuesta': 'Fecha de Respuesta',
            'medio_respuesta': 'Medio de Respuesta'
        }

        widgets = {
            'tiempo_respuesta': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': 'Ingresa el número de días hábiles'
            }),
            'fecha_maxima_respuesta': forms.DateInput(attrs={
                'class': 'form-control fecha-calculada',
                'type': 'date',
                'readonly': True,
                'placeholder': 'Se calcula automáticamente'
            }),
            'fecha_respuesta': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'placeholder': 'Selecciona la fecha de respuesta'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        tiempo_respuesta = cleaned_data.get('tiempo_respuesta')
        
        if tiempo_respuesta and tiempo_respuesta < 0:
            raise forms.ValidationError('El tiempo de respuesta no puede ser negativo.')
        
        return cleaned_data


class CrearRadicadoEnviadosForm(forms.ModelForm):
    class Meta:
        model = RadicacionEnviados
        exclude = ['radicador', 'fecha_radicacion', 'id']
        fields = '__all__'
        labels = {
            #'id': 'Número de Radicado',
            'medio_envio': 'Medio de envío',
            'tipo_comunicacion': 'Tipo de Comunicación',
            'tipo_documento': 'Tipo de Documento',
            'num_rad_llegada': 'Número de Radicado de Llegada',
            'num_rad_interno': 'Número de Radicado Interno', 
            'enviado_por': 'Enviado por',
            'requiere_respuesta': 'Requiere Respuesta',
            'tiempo_respuesta': 'Tiempo para Respuesta (días)',
            'fecha_maxima_respuesta': 'Fecha Máxima de Respuesta',
            'fecha_respuesta': 'Fecha de Respuesta',
            'recibido': 'Recibido',
        }

        widgets = {
            'tiempo_respuesta': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': 'Ingresa el número de días hábiles'
            }),
            'fecha_maxima_respuesta': forms.DateInput(attrs={
                'class': 'form-control fecha-calculada',
                'type': 'date',
                'readonly': True,
                'placeholder': 'Se calcula automáticamente'
            }),
            'fecha_respuesta': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'placeholder': 'Selecciona la fecha de respuesta'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        tiempo_respuesta = cleaned_data.get('tiempo_respuesta')
        
        if tiempo_respuesta and tiempo_respuesta < 0:
            raise forms.ValidationError('El tiempo de respuesta no puede ser negativo.')
        
        return cleaned_data


class CrearRadicadoInternosForm(forms.ModelForm):
    class Meta:
        model = RadicacionInternos
        exclude = ['radicador', 'fecha_radicacion', 'id']
        fields = '__all__'
        labels = {
            #'id': 'Número de Radicado',
            'medio_ingreso': 'Medio de ingreso',
            'tipo_comunicacion': 'Tipo de Comunicación',
            'tipo_documento': 'Tipo de Documento',
            'num_rad_llegada': 'Número de Radicado de Llegada', 
            'responsable_por_responder': 'Responsable Asignado',
            'requiere_respuesta': 'Requiere Respuesta',
            'tiempo_respuesta': 'Tiempo para Respuesta (días)',
            'fecha_maxima_respuesta': 'Fecha Máxima de Respuesta',
            'respuesta_rad_interno': 'Respuesta al Radicado Interno',
            'estado_respuesta': 'Estado de la Respuesta',
            'fecha_respuesta': 'Fecha de Respuesta',
            'medio_respuesta': 'Medio de Respuesta'
        }

        widgets = {
            'tiempo_respuesta': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': 'Ingresa el número de días hábiles'
            }),
            'fecha_maxima_respuesta': forms.DateInput(attrs={
                'class': 'form-control fecha-calculada',
                'type': 'date',
                'readonly': True,
                'placeholder': 'Se calcula automáticamente'
            }),
            'fecha_respuesta': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'placeholder': 'Selecciona la fecha de respuesta'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        tiempo_respuesta = cleaned_data.get('tiempo_respuesta')
        
        if tiempo_respuesta and tiempo_respuesta < 0:
            raise forms.ValidationError('El tiempo de respuesta no puede ser negativo.')
        
        return cleaned_data