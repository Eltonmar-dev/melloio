# users/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings # Importa as configurações
from django.db.models.signals import post_save
from django.dispatch import receiver

# Esta função é chamada automaticamente sempre que um User é salvo
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def criar_perfil_usuario(sender, instance, created, **kwargs):
    if created:
        Perfil.objects.create(user=instance)

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def salvar_perfil_usuario(sender, instance, **kwargs):
    if hasattr(instance, 'perfil'):
        instance.perfil.save()

class Perfil(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='perfil')
    plano_ativo = models.CharField(max_length=20, default='premium') # Mudamos para premium
    prompts_restantes = models.IntegerField(default=9999) # Créditos altos para teste
    foto = models.ImageField(upload_to='perfil_fotos/', null=True, blank=True)
    
    def __str__(self):
        return f"Perfil de {self.user.username}"

class Usuario(AbstractUser):
    PLANOS_CHOICES = [
        ('basico', 'Básico (15 MT) - 10 Prompts/dia'),
        ('premium', 'Premium (75 MT) - 30 Prompts/dia'),
        ('plus', 'Plus (350 MT) - 75 Prompts/dia'),
        ('ultra', 'Ultra (800 MT) - 200 Prompts/dia'),
    ]

    plano = models.CharField(max_length=10, choices=PLANOS_CHOICES, default='basico')
    prompts_restantes = models.IntegerField(default=10)
    celular = models.CharField(max_length=15, blank=True, null=True) 
    data_assinatura = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.username} ({self.get_plano_display()})"

    def reset_diario(self):
        # Configuração baseada nos novos limites que definiste
        config = {
            'basico': 10,
            'premium': 30,
            'plus': 75,
            'ultra': 200
        }
        self.prompts_restantes = config.get(self.plano, 10)
        self.save()