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
    

class UpdateRadicadosRecibidosForm(forms.ModelForm):
    class Meta:
        model = RadicacionRecibidos
        exclude = ['radicador', 'fecha_radicacion', 'id', 'tiempo_respuesta', 'fecha_maxima_respuesta', 
                   'anexos', 'observaciones', 'respuesta_rad_interno']
        fields = '__all__'

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
            })
        }



class UpdateRadicadosEnviadosForm(forms.ModelForm):
    class Meta:
        model = RadicacionEnviados
        exclude = ['id', 'fecha_radicacion', 'radicador', 'tiempo_respuesta', 'fecha_maxima_respuesta', 
                   'anexos', 'observaciones']
        fields = '__all__'

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
            })
        }


class UpdateRadicadosInternosForm(forms.ModelForm):
    class Meta:
        model = RadicacionInternos
        exclude = ['radicador', 'fecha_radicacion', 'id', 'tiempo_respuesta', 'fecha_maxima_respuesta', 
                   'anexos', 'observaciones', 'respuesta_rad_interno']
        fields = '__all__'

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
            })
        }




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
    

class CrearOficinaForm(forms.ModelForm):
    class Meta:
        model = Oficina
        fields = '__all__'
        labels = {'nombre': 'Nombre de oficina o gerencia'}


class CrearEntidadForm(forms.ModelForm):
    class Meta:
        model = Entidad
        fields = '__all__'
        labels = {'nombre': 'Nombre de la entidad'}


class CrearResponsableForm(forms.ModelForm):
    class Meta:
        model = Responsable
        fields = '__all__'


class CrearTipoDocumentoForm(forms.ModelForm):
    class Meta:
        model = TipoDocumento
        fields = '__all__'



class CrearRadicadoPqrsdForm(forms.ModelForm):
    class Meta:
        model = RadicadosRecibidosPqrsd
        exclude = ['radicador', 'fecha_radicacion', 'id', 'tipo_radicado']
        fields = '__all__'

        widgets = {
            'fecha_recibido_usuario': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'placeholder': 'Selecciona la fecha de recibido'
            }),
            'fecha_asignacion_traslado': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'placeholder': 'Selecciona la fecha de asignación o traslado'
            }),
            'fecha_evento': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'placeholder': 'Selecciona la fecha del evento'
            }),
            'hora_evento': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time',
                'placeholder': 'Selecciona la hora del evento'
            }),
            'fecha_cierre': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'placeholder': 'Selecciona la fecha de cierre'
            }),
            'vencimiento_interno': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'placeholder': 'Selecciona la fecha de vencimiento interno'
            }),
            'vencimiento_por_ley': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'placeholder': 'Selecciona la fecha de vencimiento por ley'
            }),
        }



class UpdatePqrsdRecibidosForm(forms.ModelForm):
    class Meta:
        model = RadicadosRecibidosPqrsd
        fields = [
            'fecha_cierre',
            'culpabilidad',
            'operador',
            'observaciones'
        ]

        widgets = {
            'fecha_cierre': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'placeholder': 'Selecciona la fecha de cierre'
            }),
        }



class CrearRadicadoEnviadoPqrsdForm(forms.ModelForm):
    class Meta:
        model = RadicadosEnviadosPqrsd
        exclude = ['id', 'radicador', 'fecha_radicacion',  'tipo_radicado']
        fields = [
            'asunto',
            'radicado_asociado',
            'destinatario',
        ]

        


