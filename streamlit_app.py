import streamlit as st
import os
import requests
import base64

# === SETUP HALAMAN ===
st.set_page_config(page_title="Pipin Pintarnya", page_icon="🤖")
st.title("🤖 Pipin - Asisten Misi Pintar")
st.markdown("Tanya apa pun tentang misi yang tersedia. Pipin siap bantu jawab!")

# === DATA MISI ===
missions_data = {
    "Traveloka": {
        "context_file": "misi_traveloka.txt",
        "screenshot": "screenshots/traveloka.png"
    },
    "UOB": {
        "context_file": "misi_uob.txt",
        "screenshot": "screenshots/uob.png"
    }
}

# === STATE ===
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# === PILIH MISI ===
selected_mission = st.selectbox("📌 Pilih misi dulu yuk:", [""] + list(missions_data.keys()))
if selected_mission:
    selected_topic = st.selectbox("🔍 Mau lihat apa?", ["", "Cara pengerjaan", "Rewards", "Contoh screenshot"])

    # === LOAD DOKUMEN MISI ===
    context = ""
    try:
        with open(missions_data[selected_mission]["context_file"], "r", encoding="utf-8") as file:
            context = file.read()
    except Exception as e:
        st.error(f"Gagal membaca file misi: {e}")

    # === TOPIK: SCREENSHOT ===
    if selected_topic == "Contoh screenshot":
        image_path = missions_data[selected_mission]["screenshot"]
        if os.path.exists(image_path):
            with open(image_path, "rb") as img_file:
                encoded = base64.b64encode(img_file.read()).decode()

            st.markdown("---")
            st.markdown(f"""
                <div style='text-align:center;'>
                    <img src='data:image/jpeg;base64,{encoded}' width='250'/>
                    <p><em>📸 Contoh pengerjaan misi {selected_mission}</em></p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.warning("⚠️ Gambar tidak ditemukan. Pastikan file dan path benar.")

    # === TOPIK: LAINNYA (KE OPENROUTER) ===
    elif selected_topic and context:
        user_input = st.text_input("❓ Pertanyaan kamu:", placeholder="Misal: Apakah boleh uninstall aplikasi setelah misi?")
        if user_input:
            st.chat_message("user").write(user_input)

            with st.spinner("Bot sedang mikir..."):
                try:
                    response = ask_openrouter(user_input, context, selected_mission)
                    st.session_state.chat_history.append({"role": "user", "content": user_input})
                    st.session_state.chat_history.append({"role": "assistant", "content": response})
                    st.chat_message("assistant").write(response)
                except Exception as e:
                    st.error(str(e))

    # === HISTORY ===
    for msg in st.session_state.chat_history:
        st.chat_message(msg["role"]).write(msg["content"])


# === FUNCTION: REQUEST KE OPENROUTER ===
def ask_openrouter(question, context, mission_name):
    api_key = os.getenv("OPENROUTER_API_KEY")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "https://chatbot-testing.streamlit.app",
        "X-Title": "Pipin Multi-Misi"
    }

    system_prompt = (
        f"Kamu adalah Pipin, asisten virtual yang ramah dan helpful untuk membantu user menyelesaikan misi {mission_name}. "
        "Jawablah dengan bahasa natural, sopan, dan ringkas seperti sedang chat dengan teman. "
        "Jawabanmu harus hanya berdasarkan dokumen berikut:\n\n" + context
    )

    data = {
        "model": "meta-llama/llama-4-maverick:free",
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
        raise Exception("❌ Respon tidak valid dari OpenRouter")

    return result["choices"][0]["message"]["content"]
