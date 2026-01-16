from django.db import models
from django.conf import settings
# pagamentos/models.py


class Pagamento(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    status = models.CharField(max_length=20) # 'concluido', 'pendente'
    plano_escolhido = models.CharField(max_length=20) # 'premium', 'plus'

    def save(self, *args, **kwargs):
        # Se o pagamento for salvo como concluído, atualiza o perfil
        if self.status == 'concluido':
            perfil = self.user.perfil
            perfil.plano_ativo = self.plano_escolhido
            perfil.prompts_restantes = 100 # Ou o valor do plano
            perfil.save()
        super().save(*args, **kwargs)

class Plano(models.Model):
    nome = models.CharField(max_length=50) # Ex: Básico, Premium
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    prompts = models.IntegerField() # Qtd de perguntas permitidas

    def __str__(self):
        return f"{self.nome} - {self.preco} MT"

class Transacao(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    plano_escolhido = models.CharField(max_length=20)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    comprovativo_id = models.CharField(max_length=100, blank=True) # ID do e-mola
    pago = models.BooleanField(default=False)
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario.username} - {self.plano_escolhido} ({self.valor} MT)"