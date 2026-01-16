from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='chat_index'),
    path('enviar/', views.enviar_mensagem, name='enviar_mensagem'),
    path('novo-chat/', views.novo_chat, name='novo_chat'), # Adicione esta
]