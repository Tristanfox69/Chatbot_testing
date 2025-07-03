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

# === Streamlit App Starts Here ===

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

# Update missions data, termasuk 'Rating & Review' sebagai mission
missions_data = {
    "Traveloka": {
        "context_file": "misi_traveloka.txt"
    },
    "UOB": {
        "context_file": "misi_uob.txt"
    },
    "Rating & Review": {
        # gak perlu context_file karena pake video
        "context_file": None
    }
}

selected_mission = st.selectbox("📌 Ketik atau pilih nama misinya:", [""] + list(missions_data.keys()))

if selected_mission:
    if selected_mission == "Rating & Review":
        # Kalau mission Rating & Review, hanya 1 topik Cara Pengerjaan untuk video
        st.markdown("### 🎬 Cara Pengerjaan (Video)")
        video_folder = "videos/"
        mission_prefix = selected_mission.lower().replace(" ", "_")  # misal rating_&_review -> rating_&_review

        # Cari video berdasarkan prefix
        matched_videos = sorted([
            f for f in os.listdir(video_folder)
            if f.lower().startswith(mission_prefix) and f.lower().endswith((".mp4", ".mov"))
        ])

        if matched_videos:
            for idx, vid_name in enumerate(matched_videos):
                video_path = os.path.join(video_folder, vid_name)
                st.video(video_path)
                st.caption(f"🎥 Video {idx + 1}: {vid_name}")
        else:
            st.warning("⚠️ Tidak ada video ditemukan untuk misi ini.")
    else:
        # Misi biasa, tampilkan dropdown topik
        selected_topic = st.selectbox("🔍 Mau lihat apa?", ["", "Cara Pengerjaan", "Rewards", "Contoh Screenshot", "Pertanyaan lain"])

        context = ""
        try:
            with open(missions_data[selected_mission]["context_file"], "r", encoding="utf-8") as file:
                context = file.read()
        except Exception as e:
            st.error(f"Gagal membaca file misi: {e}")

        if selected_topic == "Contoh Screenshot":
            folder = "screenshots/"
            mission_prefix = selected_mission.lower()

            matched_images = sorted([
                f for f in os.listdir(folder)
                if f.lower().startswith(mission_prefix) and f.lower().endswith((".jpg", ".jpeg", ".png"))
            ])

            st.markdown("### 📸 Contoh Screenshot")
            st.markdown("Berikut contoh Screenshot pengerjaan misi yang benar ya:")

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
                st.warning("⚠️ Tidak ada Screenshot ditemukan untuk misi ini.")

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
