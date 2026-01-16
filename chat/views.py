from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Conversa, Mensagem
from .utils import obter_configuracao_ia, obter_vetores

# Imports da IA
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

@login_required
def index(request):
    # 1. Buscar todas as conversas do usuário para a Sidebar
    conversas_historico = Conversa.objects.filter(usuario=request.user).order_by('-id')

    # 2. Verificar se o usuário clicou em um chat específico na sidebar
    chat_id = request.GET.get('chat_id')
    
    if chat_id:
        # Abre um chat específico
        conversa_atual = Conversa.objects.get(id=chat_id, usuario=request.user)
        # Desativa outros chats para manter apenas este como foco
        Conversa.objects.filter(usuario=request.user).update(ativa=False)
        conversa_atual.ativa = True
        conversa_atual.save()
    else:
        # Se não houver chat_id, tenta pegar o que já está ativo ou cria um novo
        conversa_atual, _ = Conversa.objects.get_or_create(usuario=request.user, ativa=True)

    # 3. Pegar as mensagens desta conversa específica
    historico = Mensagem.objects.filter(conversa=conversa_atual).order_by('timestamp')

    return render(request, 'chat/index.html', {
        'historico': historico,
        'conversas_historico': conversas_historico,
        'conversa_ativa_id': conversa_atual.id
    })

@login_required
def enviar_mensagem(request):
    if request.method == "POST":
        user = request.user
        pergunta = request.POST.get('mensagem')

        try:
            # Garantir que o Perfil e Plano sejam lidos corretamente
            perfil = getattr(user, 'perfil', user)
            perfil.refresh_from_db()
            
            # Verificar limite de prompts (Trava de segurança)
            if perfil.prompts_restantes <= 0:
                return JsonResponse({"status": "erro", "resposta": "Saldo de prompts esgotado. Faça um upgrade!"})

            config = obter_configuracao_ia(perfil)
            vector_db = obter_vetores()
            retriever = vector_db.as_retriever(search_kwargs={"k": 5})

            llm = ChatOpenAI(model="gpt-4o-mini", temperature=config['temperatura'])

            # Prompt que prioriza a "Personalidade" do plano
            prompt = ChatPromptTemplate.from_messages([
                ("system", "{system_instruction}"),
                ("system", "Contexto Bíblico: {context}"),
                ("human", "{input}"),
            ])

            rag_chain = (
                {"context": retriever, "input": RunnablePassthrough(), "system_instruction": lambda x: config['system_prompt']}
                | prompt
                | llm
                | StrOutputParser()
            )

            resposta_ia = rag_chain.invoke(pergunta)

            # Salvar na conversa que estiver ATIVA no momento
            conversa = Conversa.objects.get(usuario=user, ativa=True)
            Mensagem.objects.create(
                conversa=conversa,
                texto_usuario=pergunta,
                resposta_ia=resposta_ia
            )

            # Atualizar saldo de prompts
            perfil.prompts_restantes -= 1
            perfil.save()

            return JsonResponse({
                "status": "sucesso", 
                "resposta": resposta_ia,
                "restantes": perfil.prompts_restantes
            })

        except Exception as e:
            print(f"Erro: {e}")
            return JsonResponse({"status": "erro", "resposta": "Erro ao processar mensagem."})

@login_required
def novo_chat(request):
    # Desativa todas as conversas anteriores
    Conversa.objects.filter(usuario=request.user, ativa=True).update(ativa=False)
    # Cria uma nova conversa limpa e ativa
    Conversa.objects.create(usuario=request.user, ativa=True)
    return redirect('chat_index')