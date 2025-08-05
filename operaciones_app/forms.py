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
        exclude = ['operador']
        fields = [
            'fecha_solicitud', 
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
            'fecha_solicitud': 'Fecha de solicitud',
            'fecha_recogida': 'Fecha de recogida' 
        }

        widgets = {
            'fecha_solicitud': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
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

