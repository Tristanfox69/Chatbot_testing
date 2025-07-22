import streamlit as st
import os
import requests
import base64
import zipfile
from streamlit_searchbox import st_searchbox

def ask_openrouter(question, context, mission_name):
    api_key = os.getenv("OPENROUTER_API_KEY")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "https://chatbot-testing.streamlit.app",
        "X-Title": "Pipin Multi-Misi"
    }

    system_prompt = (
        f"Kamu adalah Pipin, asisten virtual yang ramah dan helpful untuk membantu user menyelesaikan misi {mission_name}.\n"
        f"Jawabanmu HARUS HANYA berdasarkan dokumen berikut:\n\n{context}\n\n"
        "Jika kamu tidak menemukan jawaban di dokumen, jawab dengan:\n"
        "'Maaf, aku tidak menemukan informasi tersebut di chat.'\n"
        "Jangan mengarang jawaban ya!"
    )

    data = {
        "model": "gpt-3.5-turbo",  # Ganti model di sini kalau mau pakai lain
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


# === Streamlit App Starts ===

st.set_page_config(page_title="Pipin Pintarnya", page_icon="🤖")

# Load logo
with open("screenshots/Pipin.png", "rb") as image_file:
    logo_base64 = base64.b64encode(image_file.read()).decode()

st.markdown(f"""
<div style='display: flex; align-items: center; gap: 10px; margin-bottom: 10px;'>
    <img src='data:image/png;base64,{logo_base64}' width='100'/>
    <h1 style='margin: 0; font-size: 2.5rem;'>Pipin - Asisten Misi Pintar</h1>
</div>
""", unsafe_allow_html=True)

st.markdown("Tanya apa pun tentang misi yang tersedia. Pipin siap bantu jawab!")

# Missions
missions_data = {
    "Traveloka": {"context_file": "misi_traveloka.txt"},
    "UOB": {"context_file": "misi_uob.txt"},
    "Rating & Review": {"context_file": None},
    "Customer Service": {"context_file": "chats.zip"}  # NEW
}

def search_mission(term: str):
    return [m for m in missions_data if term.lower() in m.lower()]

selected_mission = st_searchbox(search_function=search_mission, placeholder="🔍 Ketik nama misinya...")

if selected_mission:
    st.success(f"✅ Misi dipilih: {selected_mission}")
    context = ""

    if selected_mission == "Rating & Review":
        st.markdown("### 🎬 Cara Pengerjaan (Video)")
        folder = "videos/"
        mission_prefix = selected_mission.lower().replace(" ", "_")

        matched_videos = [f for f in os.listdir(folder) if f.lower().startswith(mission_prefix) and f.lower().endswith((".mp4", ".mov"))]
        for idx, vid in enumerate(sorted(matched_videos)):
            st.markdown(f"**🎥 Video {idx + 1}: {vid}**")
            st.video(os.path.join(folder, vid))

    elif selected_mission == "Customer Service":
        st.markdown("### 💬 Riwayat Chat WhatsApp (Customer Service)")

        try:
            with zipfile.ZipFile("chats.zip", "r") as zip_ref:
                txt_files = [f for f in zip_ref.namelist() if f.endswith(".txt")]
                if not txt_files:
                    st.error("❌ Tidak ada file .txt dalam ZIP.")
                else:
                    raw_texts = []
                    for file in txt_files:
                        with zip_ref.open(file) as f:
                            raw_texts.append(f.read().decode("utf-8", errors="ignore"))
                    context = "\n\n".join(raw_texts)
                    st.success(f"✅ {len(txt_files)} chat log dimuat dari ZIP.")

        except Exception as e:
            st.error(f"❌ Gagal membaca ZIP: {e}")

    else:
        try:
            with open(missions_data[selected_mission]["context_file"], "r", encoding="utf-8") as file:
                context = file.read()
        except Exception as e:
            st.error(f"Gagal membaca file misi: {e}")

    if context:
        user_input = st.text_input("❓ Pertanyaan kamu:")
        if user_input:
            st.chat_message("user").write(user_input)
            with st.spinner("Pipin lagi baca dokumen..."):
                try:
                    response = ask_openrouter(user_input, context, selected_mission)
                    st.chat_message("assistant").write(response)
                except Exception as e:
                    st.error(str(e))
