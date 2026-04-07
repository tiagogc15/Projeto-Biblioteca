from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('livros/', views.listar_livros, name='listar_livros'),
    path('livros/novo/', views.criar_livro, name='criar_livro'),
    path('emprestar/', views.emprestar_livro, name='emprestar'),
    path('devolver/<int:id>/', views.devolver_livro, name='devolver'),
    path('livros/editar/<int:id>/', views.editar_livro, name='editar_livro'),
    path('livros/excluir/<int:id>/', views.excluir_livro, name='excluir_livro'),
    path('registro/', views.registrar, name='registro'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('sair/', views.sair, name='sair'),
]