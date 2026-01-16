# pagamentos/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('planos/', views.lista_planos, name='lista_planos'), # Tabela de preços (15MT, 75MT...)
    path('checkout/<str:plano_tipo>/', views.checkout, name='checkout'),
    path('pagar/<str:plano_id>/', views.iniciar_pagamento, name='iniciar_pagamento'),
    path('', views.index, name='chat'),
    path('sucesso/', views.pagamento_sucesso, name='pagamento_sucesso'),
    path('planos/', views.sua_view_de_planos, name='lista_planos'),
]