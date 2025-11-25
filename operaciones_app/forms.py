from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import *
from django import forms


class LoginViewForm(forms.Form):
    username = forms.CharField(max_length=10, label="Usuario", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingresa tu usuario'}))
    password = forms.CharField(label="Contraseña", widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Ingresa tu contraseña'}))

 
class CrearSolicitudForm(forms.ModelForm):
    class Meta:
        model = SolicitudRuta
        exclude = ['operador', 'fecha_solicitud']
        fields = [
            'telefono', 
            'turno', 
            'fecha_recogida', 
            'localidad', 
            'barrio',
            'ubicacion', 
            'ruta', 
            'direccion'
        ] 

        labels = {
            'fecha_recogida': 'Fecha de recogida' 
        }

        widgets = {
            'telefono': forms.NumberInput(attrs={'type': 'number', 'class': 'form-control', 'placeholder': 'Ingrese su telefono'}),
            'turno': forms.Select(attrs={'class': 'form-check-input'}),
            'fecha_recogida': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'localidad': forms.Select(attrs={'class': 'form-control'}),
            'barrio': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese su barrio'}),
            'ubicacion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese su ubicacion'}),
            'ruta': forms.Select(attrs={'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese su direccion'}),


        }


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=40, required=True)
    last_name = forms.CharField(max_length=40, required=True)

    # Campos modelo profile
    telefono = forms.CharField(max_length=10, required=True, widget=forms.NumberInput(attrs={'type': 'number', 'class': 'form-control'}))
    direccion = forms.CharField(max_length=50, required=True)

    class Meta:
        model = User
        fields = [
            'username', 
            'email', 
            'first_name', 
            'last_name', 
            'password1', 
            'password2'
        ]


        def save(self, commit=True):
            user = super().save(commit)
            Profile.objects.create(
                user=user,
                telefono=self.cleaned_data['telefono'],
                direccion=self.cleaned_data['direccion']
            )
            return user



# class CrearOrdenChequeoForm(forms.ModelForm):
#     class Meta:
#         model = OrdenFlota
#         fields = '__all__'
#         labels = {
#             'numero_bus': 'Movil',
#         }
    


# class AgregarTurnoInspeccionForm(forms.ModelForm):
#     class Meta:
#         model = TurnoFlota
#         exclude = ['codigo_operador', 'nombre_operador' , 'orden']
#         fields = ['turno', 'ruta', 'tabla', 'instante', 'km', 'hora', 'lugar']
#         widgets = {
#             'turno': forms.Select(attrs={'class': 'form-control'}),
#             'ruta': forms.Select(attrs={'class': 'form-control'}),
#             'tabla': forms.TextInput(attrs={'class': 'form-control'}),
#             'instante': forms.Select(attrs={'class': 'form-control'}),
#             'km': forms.NumberInput(attrs={'class': 'form-control'}),
#             'hora': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
#             'lugar': forms.TextInput(attrs={'class': 'form-control'}),
#         }
    

# class DetalleChequeoForm(forms.ModelForm):
#     class Meta:
#         model = detalle_chequeo
#         fields = ['etapa', 'item', 'estado_item', 'observaciones']
#         widgets = {
#             'etapa': forms.Select(attrs={'class': 'form-control'}),
#             'item': forms.Select(attrs={'class': 'form-control'}),
#             'estado_item': forms.RadioSelect(choices=[
#                 ('OK', '✓ OK'),
#                 ('P', '⚠ Pendiente'),
#             ]),
#             'observaciones': forms.Textarea(attrs={
#                 'class': 'form-control',
#                 'rows': 3,
#                 'placeholder': 'Ingresa observaciones si es necesario'
#             }),
#         }

# class InspeccionTurnoForm(forms.ModelForm):
#     class Meta:
#         model = Inspeccion
#         fields = ['salida', 'hora', 'observaciones', 'firma']
#         widgets = {
#             'salida': forms.RadioSelect(choices=[
#                 ('P', 'Primera Salida'),
#                 ('S', 'Segunda Salida'),
#                 ('T', 'Tercera Salida'),
#             ]),
#             'hora': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
#             'observaciones': forms.Textarea(attrs={
#                 'class': 'form-control',
#                 'rows': 3,
#                 'placeholder': 'Observaciones generales de la inspección'
#             }),
#             'firma': forms.TextInput(attrs={'class': 'form-control'}),
#         }