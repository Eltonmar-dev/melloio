#!/usr/bin/env bash
# Sair imediatamente se um comando falhar
set -o errexit

# Instalar as dependências do requirements.txt
pip install -r requirements.txt

# Coletar arquivos estáticos (CSS, JS, Imagens) para a pasta staticfiles
python manage.py collectstatic --no-input

# Aplicar as migrações do banco de dados (Cria tabelas de Perfil, Chat, etc)
python manage.py migrate