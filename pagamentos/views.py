import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from .models import Plano, Transacao

# 1. LISTA DE PLANOS (Buscando do Banco de Dados)
@login_required
# pagamentos/views.py

def lista_planos(request):
    planos = Plano.objects.all()

    # Se não houver planos no banco, ele cria automaticamente agora
    if not planos.exists():
        Plano.objects.bulk_create([
            Plano(nome="basico", preco=15, prompts=10),
            Plano(nome="premium", preco=75, prompts=30),
            Plano(nome="plus", preco=350, prompts=75),
            Plano(nome="ultra", preco=800, prompts=200),
        ])
        planos = Plano.objects.all()

    return render(request, 'pagamentos/planos.html', {'planos': planos})
# 2. INICIAR PAGAMENTO (Onde estava o erro)


@login_required
def iniciar_pagamento(request, plano_id):
    plano = get_object_or_404(Plano, nome=plano_id)
    usuario = request.user
    
    # 1. VERIFICAÇÃO: O username está na lista vinda do .env?
    if usuario.username in settings.VIP_USERS:
        # Ativa o plano imediatamente
        usuario.prompts_restantes += plano.prompts
        usuario.save()
        
        # Cria a transação como paga para o histórico
        Transacao.objects.create(
            usuario=usuario,
            plano_escolhido=plano.nome,
            valor=0.0,
            pago=True
        )
        # Redireciona para o sucesso (simulado para VIPs)
        return render(request, 'pagamentos/sucesso_fake.html', {'plano': plano})

    # 2. CASO NÃO SEJA VIP: Segue para a PaySuite (quando estiver ativa)
    # ... resto do código da API PaySuite ...
    plano = get_object_or_404(Plano, nome=plano_id)
    
    usuario = request.user 
    
    # Criar registro da transação
    transacao = Transacao.objects.create(
        usuario=usuario,
        plano_escolhido=plano.nome,
        valor=plano.preco,
        pago=False
    )

    # Payload para PaySuite
    payload = {
        "apiKey": settings.PAYSUITE_API_KEY,
        "businessId": settings.PAYSUITE_ID,
        "amount": float(plano.preco),
        "currency": "MZN",
        "email": usuario.email,
        "transactionId": str(transacao.id),
        "returnUrl": "http://127.0.0.1:8000/pagamentos/sucesso/", # Ajustar para o seu domínio depois
        "cancelUrl": "http://127.0.0.1:8000/pagamentos/cancelado/",
    }

    try:
        # Chamada real para PaySuite
        response = requests.post("https://api.paysuite.co.mz/v1/checkout", json=payload)
        data = response.json()

        if data.get('url'):
            return redirect(data['url'])
        else:
            return render(request, 'pagamentos/erro.html', {"erro": "A PaySuite não devolveu uma URL válida."})

    except Exception as e:
        return render(request, 'pagamentos/erro.html', {"erro": str(e)})

# 3. WEBHOOK (Recebe a confirmação do pagamento)
@csrf_exempt
def webhook_paysuite(request):
    if request.method == "POST":
        import json
        data = json.loads(request.body) # PaySuite envia JSON no corpo da requisição
        
        transacao_id = data.get('transactionId')
        status = data.get('status')

        if status == "SUCCESS":
            transacao = Transacao.objects.get(id=transacao_id)
            if not transacao.pago: # Evitar duplicar prompts
                transacao.pago = True
                transacao.save()

                # Atualizar prompts do usuário
                usuario = transacao.usuario
                # Buscar quantos prompts este plano oferece
                plano_db = Plano.objects.get(nome=transacao.plano_escolhido)
                usuario.prompts_restantes += plano_db.prompts
                usuario.save()

            return HttpResponse(status=200)
    return HttpResponse(status=400)


@login_required
def checkout(request, plano_tipo):
    # Aqui o usuário verá o seu número e-Mola para pagar
    return render(request, 'pagamentos/checkout.html', {'plano': plano_tipo})

def index(request):
    # Aqui o usuário verá o seu número e-Mola para pagar
    return render(request, 'chat/index.html',)

@login_required
def pagamento_sucesso(request):
    perfil = request.user.perfil
    
    # Aqui fazemos a mágica: atualizamos o que o Chat vai ler
    perfil.plano_ativo = 'premium' 
    perfil.prompts_restantes = 50 
    perfil.save()
    
    return render(request, 'pagamentos/sucesso.html')