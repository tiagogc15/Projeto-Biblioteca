from django.shortcuts import render, redirect, get_object_or_404
from django.shortcuts import redirect
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from .models import Livro, Emprestimo
from .forms import LivroForm, EmprestimoForm
from .forms import RegistroForm
from .models import Livro
from .forms import LivroForm

@login_required
def home(request):
    return render(request, 'home.html')


@login_required
def listar_livros(request):
    livros = Livro.objects.all()
    return render(request, 'livros/listar.html', {'livros': livros})


@login_required
def criar_livro(request):
    form = LivroForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('listar_livros')
    return render(request, 'livros/form.html', {'form': form})


@login_required
def emprestar_livro(request):
    form = EmprestimoForm(request.POST or None)
    if form.is_valid():
        emprestimo = form.save(commit=False)
        emprestimo.usuario = request.user

        if emprestimo.livro.quantidade > 0:
            emprestimo.livro.quantidade -= 1
            emprestimo.livro.save()
            emprestimo.save()
            return redirect('listar_livros')

    return render(request, 'emprestimos/form.html', {'form': form})


@login_required
def devolver_livro(request, id):
    emp = get_object_or_404(Emprestimo, id=id)
    emp.devolvido = True
    emp.livro.quantidade += 1
    emp.livro.save()
    emp.save()
    return redirect('listar_livros')

# Create your views here.@login_required
@login_required
def editar_livro(request, id):
    livro = get_object_or_404(Livro, id=id)
    form = LivroForm(request.POST or None, instance=livro)
    if form.is_valid():
        form.save()
        return redirect('listar_livros')
    return render(request, 'livros/form.html', {'form': form})


@login_required
def excluir_livro(request, id):
    livro = get_object_or_404(Livro, id=id)
    livro.delete()
    return redirect('listar_livros')

@login_required
def registrar(request):
    form = RegistroForm(request.POST or None)

    if form.is_valid():
        form.save()
        return redirect('/')

    return render(request, 'registro.html', {'form': form})

def sair(request):
    logout(request)
    return redirect('/login/')




