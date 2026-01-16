# users/management/commands/reset_prompts.py
from django.core.management.base import BaseCommand
from users.models import Usuario

class Command(BaseCommand):
    help = 'Reseta os prompts diários de todos os usuários conforme o plano'

    def handle(self, *args, **kwargs):
        # Buscamos todos os usuários para atualizar o saldo
        usuarios = Usuario.objects.all()
        quantidade = usuarios.count()
        
        for user in usuarios:
            user.reset_diario() # Chama aquela função que criamos no models.py
            
        self.stdout.write(
            self.style.SUCCESS(f'Sucesso! Prompts de {quantidade} usuários foram resetados.')
        )