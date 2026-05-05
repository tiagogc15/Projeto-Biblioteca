from django.shortcuts import render, redirect, get_object_or_404
from django.shortcuts import redirect
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from .models import Livro, Emprestimo
from .forms import LivroForm, EmprestimoForm
from .forms import RegistroForm
from .models import Livro
from .forms import LivroForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, redirect
from django.utils import timezone
from .models import Emprestimo
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from django.contrib.auth.models import User
from django.http import HttpResponse


def criar_admin(request):
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser(
            username='admin',
            email='admin@email.com',
            password='123456'
        )
        return HttpResponse("Admin criado com sucesso!")
    return HttpResponse("Admin já existe!")

def is_admin(user):
    return user.is_staff
@login_required
def home(request):
    total_livros = Livro.objects.count()

    # 🔥 SOMA DAS QUANTIDADES
    disponiveis = Livro.objects.aggregate(total=Sum('quantidade'))['total'] or 0

    # 🔥 TOTAL EMPRESTADO
    emprestados = Emprestimo.objects.filter(data_devolucao__isnull=True).count()

    return render(request, 'home.html', {
        'total_livros': total_livros,
        'disponiveis': disponiveis,
        'emprestados': emprestados
    })



@login_required
def listar_livros(request):
    livros = Livro.objects.all()
    return render(request, 'livros/listar.html', {'livros': livros})


@user_passes_test(is_admin)
@login_required
def criar_livro(request):
    form = LivroForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('listar_livros')
    return render(request, 'livros/form.html', {'form': form})


@login_required
def emprestar_livro(request):
    livro_id = request.GET.get('livro')

    if not livro_id:
        messages.error(request, "Selecione um livro válido")
        return redirect('/livros/')

    livro = Livro.objects.get(id=livro_id)

    ja_tem = Emprestimo.objects.filter(
        usuario=request.user,
        livro=livro,
        data_devolucao__isnull=True
    ).exists()

    if ja_tem:
        messages.warning(request, "Você já pegou esse livro!")
        return redirect('/livros/')

    if livro.quantidade > 0:
        livro.quantidade -= 1
        livro.save()

        Emprestimo.objects.create(
            usuario=request.user,
            livro=livro
        )

        messages.success(request, "Livro reservado com sucesso!")
    else:
        messages.error(request, "Livro indisponível!")

    return redirect('/livros/')


@login_required
def devolver_livro(request, id):
    emprestimo = get_object_or_404(Emprestimo, id=id)

    # 🔥 segurança: só dono ou admin
    if emprestimo.usuario != request.user and not request.user.is_staff:
        return redirect('/')

    emprestimo.devolvido = True
    emprestimo.data_devolucao = timezone.now()
    emprestimo.save()

    livro = emprestimo.livro
    livro.quantidade += 1
    livro.save()

    return redirect('/meus/')

# Create your views here.@login_required
@user_passes_test(is_admin)
@login_required
def editar_livro(request, id):
    livro = get_object_or_404(Livro, id=id)
    form = LivroForm(request.POST or None, instance=livro)
    if form.is_valid():
        form.save()
        return redirect('listar_livros')
    return render(request, 'livros/form.html', {'form': form})


@user_passes_test(is_admin)
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

def registro(request):
    form = RegistroForm(request.POST or None)
    if form.is_valid():
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['password'])
        user.save()
        login(request, user)
        return redirect('/')
    return render(request, 'registro.html', {'form': form})

@login_required
def meus_emprestimos(request):
    emprestimos = Emprestimo.objects.filter(usuario=request.user)

    return render(request, 'meus_emprestimos.html', {
        'emprestimos': emprestimos
    })

@login_required
def emprestar_livro(request):
    livro_id = request.GET.get('livro')
    livro = Livro.objects.get(id=livro_id)

    ja_tem = Emprestimo.objects.filter(
        usuario=request.user,
        livro=livro,
        data_devolucao__isnull=True
    ).exists()

    if ja_tem:
        return redirect('/livros/')  

    if livro.quantidade > 0:
        livro.quantidade -= 1
        livro.save()

        Emprestimo.objects.create(
            usuario=request.user,
            livro=livro
        )

    return redirect('/livros/')








