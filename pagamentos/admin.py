from django.contrib import admin
from .models import Transacao

@admin.register(Transacao)
class TransacaoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'plano_escolhido', 'valor', 'pago', 'data_criacao')
    list_filter = ('pago', 'plano_escolhido')