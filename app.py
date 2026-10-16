from openai import AzureOpenAI
from pypdf import PdfReader
import streamlit as st

# Configuração inicial da página Streamlit
st.set_page_config(
    page_title="ChatBot RAG - Microsoft Foundry", page_icon="🤖", layout="wide"
)

# 1. Interface e Estilo (CSS Customizado para Borda Profissional)
st.markdown(
    """
    <style>
    /* Estilização da caixa principal (Container/Borda) */
    .block-container {
        border: 2px solid #2b5b84;
        border-radius: 15px;
        padding: 2.5rem 2.5rem 2.5rem 2.5rem;
        background-color: #ffffff;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
    }
    /* Estilização da Barra Lateral */
    .stSidebar {
        background-color: #f7f9fa;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# 2. Configuração da API (Microsoft Foundry / Azure OpenAI)
API_KEY = "6t2pTNsmNafDyo53MDAFIrvvQRBZXP7dLcr5j3TLxMS34LQVq3ZUJQQJ99CHACHYHv6XJ3w3AAAAACOGT7os"
MODEL_NAME = "gpt-4.1-mini"  # Nome da Implantação (Deployment)
ENDPOINT = "https://marcelomaffeis-05082026-resource.services.ai.azure.com/"

# Inicialização do cliente Azure OpenAI
client = AzureOpenAI(
    api_key=API_KEY, api_version="2024-02-01", azure_endpoint=ENDPOINT
)

# Título do Aplicativo
st.title("🤖 ChatBot Acadêmico com RAG")
st.markdown(
    "Assistente inteligente integrado ao **Microsoft Foundry** com suporte a upload de documentos para contexto."
)

# 3. Upload de Arquivos e Sistema RAG na Barra Lateral
with st.sidebar:
    st.header("📁 Base de Conhecimento (RAG)")
    uploaded_file = st.file_uploader(
        "Envie um arquivo PDF ou TXT", type=["pdf", "txt"]
    )

    document_text = ""
    if uploaded_file is not None:
        file_extension = uploaded_file.name.split(".")[-1].lower()

        if file_extension == "pdf":
            try:
                reader = PdfReader(uploaded_file)
                for page in reader.pages:
                    text = page.extract_text()
                    if text:
                        document_text += text + "\n"
                st.success(f"PDF carregado: **{uploaded_file.name}**")
            except Exception as e:
                st.error(f"Erro ao ler o arquivo PDF: {e}")

        elif file_extension == "txt":
            try:
                document_text = uploaded_file.read().decode("utf-8")
                st.success(f"TXT carregado: **{uploaded_file.name}**")
            except Exception as e:
                st.error(f"Erro ao ler o arquivo TXT: {e}")

        # Mostrar prévia do texto extraído
        if document_text:
            with st.expander("Ver trecho do conteúdo extraído"):
                st.text_area(
                    "Contexto RAG", document_text[:1500] + "...", height=150
                )

    st.markdown("---")
    if st.button("🗑️ Limpar Conversa"):
        st.session_state.messages = []
        st.rerun()

# 4. Lógica de Chat e Histórico (st.session_state)
if "messages" not in st.session_state:
    st.session_state.messages = []

# Exibir mensagens anteriores do histórico
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Capturar input do usuário
if prompt := st.chat_input("Faça uma pergunta sobre o documento ou geral..."):
    # Adicionar mensagem do usuário ao histórico
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Construção do Prompt do Sistema (RAG Context Injection)
    system_prompt = (
        "Você é um assistente virtual acadêmico prestativo e preciso."
    )
    if document_text:
        system_prompt += f"""
        
        Utilize estritamente o seguinte contexto extraído do documento enviado pelo usuário para fundamentar e responder às perguntas:
        --- INÍCIO DO DOCUMENTO ---
        {document_text}
        --- FIM DO DOCUMENTO ---
        
        Caso a resposta não esteja explícita no documento, avise o usuário e complemente com seu conhecimento geral de forma prudente.
        """

    # Montar payload de mensagens para a API
    messages_payload = [{"role": "system", "content": system_prompt}]
    for msg in st.session_state.messages:
        messages_payload.append(
            {"role": msg["role"], "content": msg["content"]}
        )

    # Chamada da API do Microsoft Foundry
    with st.chat_message("assistant"):
        with st.spinner("Analisando e gerando resposta..."):
            try:
                response = client.chat.completions.create(
                    model=MODEL_NAME, messages=messages_payload, temperature=0.3
                )
                assistant_response = response.choices[0].message.content
                st.markdown(assistant_response)

                # Salvar resposta no histórico
                st.session_state.messages.append(
                    {"role": "assistant", "content": assistant_response}
                )
            except Exception as e:
                st.error(f"Erro ao comunicar com o Microsoft Foundry: {e}")
