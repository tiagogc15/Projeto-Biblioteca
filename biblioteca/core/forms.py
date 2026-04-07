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
        fields = ['livro', 'data_emprestimo', 'data_devolucao']
        
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class RegistroForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']