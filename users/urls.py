# users/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect
from . import views


urlpatterns = [
    # O name='login' aqui é o que o LOGIN_URL do settings procura
    path('', lambda request: redirect('perfil')),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('perfil/', views.perfil_view, name='perfil'),
    path('cadastro/', views.cadastro, name='cadastro'),
    path('planos', views.lista_planos, name='lista_planos'),
]