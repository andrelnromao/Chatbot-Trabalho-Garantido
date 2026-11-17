
import os # Biblioteca para acessar variáveis de ambiente
import streamlit as st # Framework para criar a interface web do chatbot
from dotenv import load_dotenv # Função que carrega as variáveis do arquivo .env
from langchain_community.document_loaders import PyPDFLoader # Carrega documentos em formato PDF
from langchain_text_splitters import RecursiveCharacterTextSplitter # Divide textos longos em trechos menores (chunks)
from langchain_chroma import Chroma # Banco de dados vetorial utilizado no projeto
from langchain_groq import ChatGroq # Integra o Python à API da Groq para utilizar o LLM
from langchain_huggingface import HuggingFaceEmbeddings # Gera embeddings utilizando modelos do Hugging Face

#1. CONFIGURAÇÃO DA API GRPQ
#Carrega as variaveis armazenadas no arquivo .env
load_dotenv()

#Verifica se a chave API esta disponivel
if not os.getenv("GROQ_API_KEY"):
    st.error('Configure a chave API_GROQ no arquivo .env')
    st.stop() # interrompe a execução

#2. INTERFACE INICIAL
st.title('Chatbot Trabalho Garantido')
st.write('Faça perguntas sobre o edital do programa')

#Para testar: phyton -m streamlit run app.py
#

#3. PREPARAÇÃO DO RAG

# Armazena e cache recursos criados pela função
# Evita reconstruir o banco vetorial a cata ingeração
@st.cache_resource
def iniciar_rag():

    # Carrega o arquivo PDF
    carregador = pyPDFLoader("Trabalho-garantido-edital.pdf")

    #Lê o PDF e transforma seu conteúdo chunks
    documentos = carrregador.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,    # Tamanho maximo de cada chunk em caracteres
        chunk_overlap=200   # Sobreposição entre os chunks
    )
    chunks = splitter.split_documents(documentos)

    # Carrega o modelo do embeddings do Hugging Face.
    embeddings = HuggingFaceEmbeddings(
        model_name-"sentence-transformers/all=MiniLM-L6-v2"
    )

    # Cria o banco vetorial a partir dos chunks e armazena no Chroma

    banco = Chroma.from_documents(
        documents=chunks,
        embeddings=embeddings
    )

    retriever = banco.as_retriever(search_kwargs=("k": 5))

    # Configura o modelo de linguagem acessado pela Groq
    # O LLM será responsavel por gerar as respostas com base nos trechos

    llm = ChatGroq(model="openai/gpt-oss-120b",temperature=0)

    return retriever, llm

    # INICIALIZAÇÃO DO CHATBOT

    try:

        #Exibe uma mensagem enquanto o RAG é preparado
with st.spinner("Preparando o chatbot..."):

        # Executa a função e recebe o retriever e o LLM
        retriever, llm = iniciar_rag()

except Exception as erro:

    # Exibe a mensagem caso ocorra algum erro
    st.error(f"Erro ao iniciar: {erro}")

    # Interrompe a aplicação
    st.stop()


#HISTÓRICO DE MENSAGENS

# Verifica se a lista de mensagens já existe na sessão
if "mensagens" not in st.session_state:

    # Cria uma lista vazia para armazenar o histórico
    st.session_state.mensagens = []


# Percorre as mensagens armazenadas no histórico
for mensagem in st.session_state.mensagens:

    # "user" representa o usuário
    # "assistant" representa o chatbot
    with st.chat_message(mensagem["role"]):

        # Exibe o conteúdo da mensagem na interface
        st.markdown(mensagem["content"])


# Exibe o campo para o usuário digitar sua pergunta
if pergunta := st.chat_input("Digite sua pergunta..."):

    # Exibe a pergunta na interface do chatbot
    with st.chat_message("user"):
        st.write(pergunta)

    # Armazena a pergunta no histórico de mensagens
    st.session_state.mensagens.append({"role": "user","content": pergunta})


    # Cria o espaço para a resposta do chatbot
    with st.chat_message("assistant"):

        # Exibe uma mensagem durante o processamento
        with st.spinner("Consultando o edital..."):

            try:
                # Recupera os chunks relevantes para a pergunta
                documentos = retriever.invoke(pergunta)

                # Reúne os textos recuperados em um único contexto
                contexto = "\n\n".join(
                    doc.page_content for doc in documentos
                )

                # Monta as instruções enviadas ao modelo de linguagem
                prompt = f"""
                Você é um assistente do Programa Trabalho Garantido.

                Responda utilizando apenas as informações
                do edital fornecidas abaixo.

                Se não encontrar a resposta, informe que
                a informação não foi localizada no edital.

                Contexto:
                {contexto}

                Pergunta:
                {pergunta}
                """

                # Envia o prompt ao LLM e recebe a resposta
                resposta = llm.invoke(prompt).content

                # Exibe a resposta na interface
                st.markdown(resposta)

                # Armazena a resposta no histórico
                st.session_state.mensagens.append({
                    "role": "assistant",
                    "content": resposta
                })

            except Exception as erro:
                # Exibe uma mensagem caso ocorra algum erro
                st.error(f"Erro ao responder: {erro}")
                

Remover todos os anúncios

Remover todos os anúncios
