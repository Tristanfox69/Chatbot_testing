import streamlit as st
import os
import requests

# Setup Streamlit
st.set_page_config(page_title="MisiBot Traveloka", page_icon="🤖")
st.title("🤖 MisiBot Traveloka")
st.markdown("Tanya apa pun tentang misi Traveloka. Bot akan jawab berdasarkan dokumen yang sudah disiapkan.")
st.write("🔍 API Key loaded?", os.getenv("OPENROUTER_API_KEY") is not None)

# Load dokumentasi misi
with open("misi_traveloka.txt", "r", encoding="utf-8") as file:
    mission_context = file.read()

# Cek histori chat
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Tampilkan histori sebelumnya
for msg in st.session_state.chat_history:
    st.chat_message(msg["role"]).write(msg["content"])

# Fungsi untuk kirim pertanyaan
def ask_openrouter(question, context):
    api_key = os.getenv("OPENROUTER_API_KEY")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "https://chatbot-testing.streamlit.app",
        "X-Title": "Traveloka MisiBot"
    }

    # Deteksi apakah pertanyaan berhubungan dengan misi
    misi_keywords = [
        "misi", "izin", "boleh", "policy", "aturan", "peraturan",
        "uninstall", "akses", "cuti", "tim", "internal", "data", "perusahaan"
    ]
    related_to_mission = any(keyword in question.lower() for keyword in misi_keywords)

    if related_to_mission:
        system_prompt = "Jawab hanya berdasarkan dokumen berikut:\n" + context
    else:
        system_prompt = "Kamu adalah asisten ramah dari Traveloka. Jawab dengan sopan dan bantu user sebaik mungkin."

    data = {
        "model": "deepseek/deepseek-r1-0528:free",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question}
        ]
    }

    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)

    if response.status_code != 200:
        raise Exception(f"❌ Status {response.status_code}: {response.text}")

    result = response.json()
    if "choices" not in result:
        raise Exception(f"❌ Respon tidak valid dari OpenRouter:\n{result}")

    return result["choices"][0]["message"]["content"]

# Input user
user_input = st.text_input("❓ Pertanyaan kamu:", placeholder="Misal: Boleh uninstall aplikasinya?")

# Proses input
if user_input:
    st.chat_message("user").write(user_input)
    with st.spinner("Bot sedang mikir..."):
        try:
            response = ask_openrouter(user_input, mission_context)
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            st.session_state.chat_history.append({"role": "assistant", "content": response})
            st.chat_message("assistant").write(response)
        except Exception as e:
            st.error(str(e))

