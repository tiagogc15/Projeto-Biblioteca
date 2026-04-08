from django import forms
from .models import Livro, Emprestimo
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class LivroForm(forms.ModelForm):
    class Meta:
        model = Livro
        fields = '__all__'


class EmprestimoForm(forms.ModelForm):
    class Meta:
        model = Emprestimo
        fields = ['livro']
        
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class RegistroForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        

from django import forms
from django.contrib.auth.models import User

class RegistroForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'password']

    def clean_username(self):
        username = self.cleaned_data.get('username')

        if not username.isalnum():
            raise forms.ValidationError("Use apenas letras e números!")

        return username