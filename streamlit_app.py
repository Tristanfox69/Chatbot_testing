import streamlit as st
import os
import requests

st.set_page_config(page_title="MisiBot Traveloka", page_icon="🤖")
st.title("🤖 MisiBot Traveloka")
st.markdown("Tanya apa pun tentang misi Traveloka. Bot akan jawab berdasarkan dokumen yang sudah disiapkan.")

# Load dokumentasi misi
with open("misi_traveloka.txt", "r", encoding="utf-8") as file:
    mission_context = file.read()

# Fungsi buat kirim ke OpenRouter langsung
def ask_openrouter(question, context):
    api_key = os.getenv("OPENROUTER_API_KEY")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "https://chatbot-testing.streamlit.app",
        "X-Title": "Traveloka MisiBot"
    }
    data = {
        "model": "openai/gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "Jawab berdasarkan dokumen berikut:\n" + context},
            {"role": "user", "content": question}
        ]
    }
    res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
    return res.json()["choices"][0]["message"]["content"]

# Input
user_input = st.text_input("❓ Pertanyaan kamu:", placeholder="Misal: Boleh uninstall aplikasinya?")

if user_input:
    with st.spinner("Bot sedang mikir..."):
        try:
            response = ask_openrouter(user_input, mission_context)
            st.success(response)
        except Exception as e:
            st.error(f"Gagal menjawab: {e}")
