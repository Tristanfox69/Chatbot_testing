import streamlit as st
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
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

# Create vector store
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
db = FAISS.from_documents(texts, embeddings)
retriever = db.as_retriever()

# QA Chain
qa = RetrievalQA.from_chain_type(
    llm=ChatOpenAI(
        temperature=0,
        openai_api_key=os.getenv("OPENROUTER_API_KEY"),
        openai_api_base="https://openrouter.ai/api/v1",
        model_name="openai/gpt-3.5-turbo"
    ),
    chain_type="stuff",
    retriever=retriever
)

# Input form
query = st.text_input("❓ Pertanyaan kamu:", placeholder="Misal: Kalau aku udah pernah install Traveloka gimana?")
if query:
    with st.spinner("Menjawab..."):
        result = qa.run(query)
        st.success(result)
