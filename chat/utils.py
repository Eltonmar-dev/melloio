import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

def obter_configuracao_ia(perfil):
    # Supondo que o perfil tenha um atributo 'plano' ou 'plano_ativo'
    plano = getattr(perfil, 'plano_ativo', 'free').lower()
    

    if plano == 'premium':
        return {
            "max_tokens_saida": 800,
            "temperatura": 0.5,
            "system_prompt": (
                "Tu és um Instrutor Bíblico Avançado e didático. "
                "Ensina as Escrituras com clareza e profundidade prática. "
                "Apresenta o significado do texto, tema central e contexto histórico básico."
            )
        }

    elif plano == 'plus':
        return {
            "max_tokens_saida": 1500,
            "temperatura": 0.4,
            "system_prompt": (
                "Tu és um Teólogo e Historiador Bíblico completo. "
                "Apresenta o pano de fundo histórico, político e religioso. "
                "Explica termos em Hebraico/Grego e conexões entre os Testamentos."
            )
        }

    elif plano in ['ultra', 'vip']:
        return {
            "max_tokens_saida": 3000,
            "temperatura": 0.2,
            "system_prompt": (
                "Tu és um Ph.D em Exegese Bíblica e Teologia Sistemática. "
                "Analisa o texto no original, discute variantes textuais, arqueologia "
                "e contribuições teológicas clássicas com rigor acadêmico."
            )
        }

    # BÁSICO OU FREE
    return {
        "max_tokens_saida": 600,
        "temperatura": 0.7,
        "system_prompt": (
            "Tu és um Instrutor Bíblico Avançado e didático. "
                "Ensina as Escrituras com clareza e profundidade prática. "
                "Apresenta o significado do texto, tema central e contexto histórico alto."
        )
    }

def processar_biblia():
    caminho_pdf = "conhecimento/biblia_sagrada.pdf"
    if not os.path.exists(caminho_pdf):
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho_pdf}")
        
    loader = PyPDFLoader(caminho_pdf)
    documentos = loader.load()
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    textos = text_splitter.split_documents(documentos)
    
    embeddings = OpenAIEmbeddings()
    vector_db = Chroma.from_documents(
        documents=textos, 
        embedding=embeddings, 
        persist_directory="db_vector"
    )
    return vector_db

def obter_vetores():
    embeddings = OpenAIEmbeddings()
    if os.path.exists("db_vector"):
        return Chroma(persist_directory="db_vector", embedding_function=embeddings)
    else:
        return processar_biblia()