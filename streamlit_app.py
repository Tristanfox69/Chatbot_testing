import streamlit as st
import os
import requests
import base64

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

# Set up Streamlit page
st.set_page_config(page_title="Pipin Pintarnya", page_icon="🤖")

# Load logo image
with open("screenshots/Pipin.png", "rb") as image_file:
    logo_base64 = base64.b64encode(image_file.read()).decode()

st.markdown(f"""
<div style='display: flex; align-items: center; gap: 10px; margin-bottom: 10px;'>
    <img src='data:image/png;base64,{logo_base64}' width='100'/>
    <h1 style='margin: 0; font-size: 2.5rem;'>Pipin - Asisten Misi Pintar</h1>
</div>
""", unsafe_allow_html=True)

st.markdown("Tanya apa pun tentang misi yang tersedia. Pipin siap bantu jawab!")

# Available missions
missions_data = {
    "Traveloka": {"context_file": "misi_traveloka.txt"},
    "UOB": {"context_file": "misi_uob.txt"}
}

available_missions = list(missions_data.keys())
typed_input = st.text_input("📌 Ketik nama misinya (misal: Traveloka atau UOB):")

# Filter suggestions
suggestions = [m for m in available_missions if typed_input.lower() in m.lower()] if typed_input else []
selected_mission = None

# Show suggestions as clickable buttons
if suggestions and typed_input and typed_input.strip().title() not in missions_data:
    st.markdown("**🔍 Pipin nemu ini nih:**")
    for m in suggestions:
        if st.button(f"➡️ {m}"):
            selected_mission = m
else:
    if typed_input.strip().title() in missions_data:
        selected_mission = typed_input.strip().title()

# Proceed if a mission is selected
if selected_mission:
    selected_topic = st.selectbox("🔍 Mau lihat apa?", ["", "Cara Pengerjaan", "Rewards", "Contoh screenshot", "Pertanyaan lain"])

    context = ""
    try:
        with open(missions_data[selected_mission]["context_file"], "r", encoding="utf-8") as file:
            context = file.read()
    except Exception as e:
        st.error(f"Gagal membaca file misi: {e}")

    if selected_topic == "Contoh screenshot":
        folder = "screenshots/"
        mission_prefix = selected_mission.lower()

        matched_images = sorted([
            f for f in os.listdir(folder)
            if f.lower().startswith(mission_prefix) and f.lower().endswith((".jpg", ".jpeg", ".png"))
        ])

        st.markdown("### 📸 Contoh Screenshot")
        st.markdown("Berikut contoh screenshot pengerjaan misi yang benar ya:")

        if matched_images:
            if len(matched_images) == 1:
                image_path = os.path.join(folder, matched_images[0])
                with open(image_path, "rb") as img_file:
                    encoded = base64.b64encode(img_file.read()).decode()

                st.markdown("---")
                st.markdown(f"""
                    <div style='text-align:center;'>
                        <img src='data:image/jpeg;base64,{encoded}' width='300'/>
                        <p><em>📸 Contoh SS1 yang benar</em></p>
                    </div>
                """, unsafe_allow_html=True)
            else:
                cols = st.columns(2)
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

    elif selected_topic and context:
        user_input = st.text_input("❓ Pertanyaan kamu:", placeholder="Misal: Apa aja langkah-langkahnya?")
        if user_input:
            st.chat_message("user").write(user_input)

            with st.spinner("Pipin pusing mikir dulu ya ..."):
                try:
                    response = ask_openrouter(user_input, context, selected_mission)
                    st.chat_message("assistant").write(response)
                except Exception as e:
                    st.error(str(e))
elif typed_input:
    st.warning("⚠️ Belum ketemu misi yang cocok. Coba ketik lebih lengkap.")
