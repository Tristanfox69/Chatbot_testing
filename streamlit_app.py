import streamlit as st
from langchain_community.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
import os

st.set_page_config(page_title="MisiBot - Traveloka", page_icon="🤖")
st.title("🤖 MisiBot Traveloka")
st.markdown("Tanya apa pun tentang misi Traveloka, dan bot akan bantu jawab berdasarkan dokumen resminya.")

# Load and split the document
loader = TextLoader("misi_traveloka.txt")
docs = loader.load()
text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
texts = text_splitter.split_documents(docs)

# Create vector store with HuggingFace Embeddings
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
db = FAISS.from_documents(texts, embeddings)
retriever = db.as_retriever()

# Chat model via OpenRouter
llm = ChatOpenAI(
    temperature=0,
    model="openai/gpt-3.5-turbo",
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

# QA Chain
qa = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=retriever
)

# Input form
query = st.text_input("❓ Pertanyaan kamu:", placeholder="Misal: Kalau aku udah pernah install Traveloka gimana?")
if query:
    with st.spinner("Menjawab..."):
        result = qa.run(query)
        st.success(result)
