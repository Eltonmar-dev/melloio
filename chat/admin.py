from django.contrib import admin
from .models import Conversa, Mensagem

@admin.register(Conversa)
class ConversaAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'titulo', 'criada_em', 'ativa')
    list_filter = ('ativa', 'criada_em')
    search_fields = ('usuario__username', 'titulo')

@admin.register(Mensagem)
class MensagemAdmin(admin.ModelAdmin):
    # 'conversa__usuario' busca o nome do usuário através da relação com a conversa
    list_display = ('get_usuario', 'conversa', 'timestamp')
    readonly_fields = ('timestamp',) # Nome corrigido de data_envio para timestamp

    def get_usuario(self, obj):
        return obj.conversa.usuario
    get_usuario.short_description = 'Usuário'