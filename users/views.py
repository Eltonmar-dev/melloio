
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views import generic
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario  # <--- IMPORTANTE: Importar o seu modelo customizado

class CadastroForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Usuario
        # Adicionamos o campo email que geralmente não vem no UserCreationForm padrão
        fields = UserCreationForm.Meta.fields + ('email',)

def cadastro(request):
    if request.method == "POST":
        form = CadastroForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = CadastroForm()
    # Removida a aspa simples que estava causando o SyntaxError na linha 25
    return render(request, 'users/cadastro.html', {'form': form})
# Esta é a função que o erro diz que está a faltar:
# users/views.py
from .models import Perfil

from django.contrib import messages # Importe isso

@login_required
def perfil_view(request):
    perfil, created = Perfil.objects.get_or_create(user=request.user)
    
    if request.method == "POST":
        nome = request.POST.get('nome')
        if nome:
            request.user.first_name = nome
            request.user.save()
            
        if 'foto' in request.FILES:
            perfil.foto = request.FILES['foto']
            
        perfil.save()
        messages.success(request, "Perfil atualizado com sucesso!") # Mensagem de sucesso
        return redirect('perfil')

    return render(request, 'users/perfil.html', {'perfil': perfil})

@login_required
def lista_planos(request):
    # Por enquanto, apenas renderiza uma página de planos
    return render(request, 'pagamentos/planos.html')