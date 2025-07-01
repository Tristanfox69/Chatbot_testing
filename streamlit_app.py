import streamlit as st
import os
import requests
import base64

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

# === SETUP HALAMAN ===
st.set_page_config(page_title="Pipin Pintarnya", page_icon="🤖")
st.title("🤖 Pipin - Asisten Misi Pintar")
st.markdown("Tanya apa pun tentang misi yang tersedia. Pipin siap bantu jawab!")

# === DATA MISI ===
missions_data = {
    "Traveloka": {
        "context_file": "misi_traveloka.txt"
    },
    "UOB": {
        "context_file": "misi_uob.txt"
    }
}

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

    # === TOPIK: SCREENSHOT MULTI FILE, SIDE BY SIDE ===
    if selected_topic == "Contoh Screenshot":
        folder = "screenshots/"
        mission_prefix = selected_mission.lower()

        matched_images = sorted([
            f for f in os.listdir(folder)
            if f.lower().startswith(mission_prefix) and f.lower().endswith((".jpg", ".jpeg", ".png"))
        ])

        if matched_images:
            cols = st.columns(2)  # 2 kolom sejajar
            for idx, img_name in enumerate(matched_images):
                image_path = os.path.join(folder, img_name)
                with open(image_path, "rb") as img_file:
                    encoded = base64.b64encode(img_file.read()).decode()

                with cols[idx % 2]:
                    st.markdown(f"""
                        <div style='text-align:center;'>
                            <img src='data:image/jpeg;base64,{encoded}' width='250'/>
                            <p><em>📸 Contoh SS{idx + 1} yang benar</em></p>
                        </div>
                    """, unsafe_allow_html=True)
        else:
            st.warning("⚠️ Tidak ada screenshot ditemukan untuk misi ini.")

    # === TOPIK: Q&A KE OPENROUTER ===
    elif selected_topic and context:
        user_input = st.text_input("❓ Pertanyaan kamu:", placeholder="Misal: Apakah boleh uninstall aplikasi setelah misi?")
        if user_input:
            st.chat_message("user").write(user_input)

            with st.spinner("Bot sedang mikir..."):
                try:
                    response = ask_openrouter(user_input, context, selected_mission)
                    st.chat_message("assistant").write(response)
                except Exception as e:
                    st.error(str(e))
