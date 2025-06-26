import streamlit as st
import os
import requests

st.write("🔍 API Key loaded?", os.getenv("OPENROUTER_API_KEY") is not None)
st.set_page_config(page_title="MisiBot Traveloka", page_icon="🤖")
st.title("🤖 MisiBot Traveloka")
st.markdown("Tanya apa pun tentang misi Traveloka. Bot akan jawab berdasarkan dokumen yang sudah disiapkan.")

# Load dokumentasi misi
with open("misi_traveloka.txt", "r", encoding="utf-8") as file:
    mission_context = file.read()

# Fungsi buat kirim pertanyaan ke OpenRouter API
def ask_openrouter(question, context):
    api_key = os.getenv("OPENROUTER_API_KEY")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "https://chatbot-testing.streamlit.app",  # opsional tapi disarankan
        "X-Title": "Traveloka MisiBot"
    }
    data = {
        "model": "openai/gpt-3.5-turbo",  # pastikan ini sesuai dengan model yang tersedia di akun lo
        "messages": [
            {"role": "system", "content": "Jawab hanya berdasarkan dokumen berikut:\n" + context},
            {"role": "user", "content": question}
        ]
    }
    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)

    # Cek error dari OpenRouter
    if response.status_code != 200:
        raise Exception(f"❌ Status {response.status_code}: {response.text}")

    result = response.json()
    if "choices" not in result:
        raise Exception(f"❌ Respon tidak valid dari OpenRouter:\n{result}")

    return result["choices"][0]["message"]["content"]

# Input dari user
user_input = st.text_input("❓ Pertanyaan kamu:", placeholder="Misal: Boleh uninstall aplikasinya?")

if user_input:
    with st.spinner("Bot sedang mikir..."):
        try:
            response = ask_openrouter(user_input, mission_context)
            st.success(response)
        except Exception as e:
            st.error(str(e))

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Tampilkan histori
for msg in st.session_state.chat_history:
    st.chat_message(msg["role"]).write(msg["content"])

# Kalau ada input baru
if user_input:
    with st.spinner("Bot sedang mikir..."):
        try:
            response = ask_openrouter(user_input, mission_context)
            # Tambahin ke histori
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            st.session_state.chat_history.append({"role": "assistant", "content": response})
            st.chat_message("assistant").write(response)
        except Exception as e:
            st.error(str(e))

