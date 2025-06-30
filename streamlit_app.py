import streamlit as st
import os
import requests
import base64

# === SETUP HALAMAN ===
st.set_page_config(page_title="Pipin Pintarnya", page_icon="🤖")
st.title("🤖 MisiBot Traveloka")
st.markdown("Tanya apa pun tentang misi Traveloka. Pipin sian menjawab pertanyaan berdasarkan yang Pipin bisa.")
st.write("🔍 API Key loaded?", os.getenv("OPENROUTER_API_KEY") is not None)

# === LOAD DOKUMEN MISI ===
with open("misi_traveloka.txt", "r", encoding="utf-8") as file:
    mission_context = file.read()

# === CEK CHAT HISTORY ===
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# === TAMPILKAN CHAT SEBELUMNYA ===
for msg in st.session_state.chat_history:
    st.chat_message(msg["role"]).write(msg["content"])

# === FUNCTION UNTUK REQUEST KE OPENROUTER ===
def ask_openrouter(question, context):
    api_key = os.getenv("OPENROUTER_API_KEY")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "https://chatbot-testing.streamlit.app",
        "X-Title": "Traveloka MisiBot"
    }

    # Deteksi kata kunci
    misi_keywords = [
        "misi", "izin", "boleh", "policy", "aturan", "peraturan",
        "uninstall", "akses", "cuti", "tim", "internal", "data", "perusahaan"
    ]
    screenshot_keywords = ["screenshot", "ss", "screen shot", "contoh gambar", "contoh tampilan"]

    related_to_mission = any(k in question.lower() for k in misi_keywords)

    # Buat system prompt
    if related_to_mission:
        system_prompt = (
    "Kamu adalah Pipin, asisten virtual yang ramah dan helpful untuk membantu user menyelesaikan misi Traveloka. "
    "Jawablah dengan bahasa natural, sopan, dan ringkas seperti sedang chat dengan teman. "
    "Gunakan hanya informasi yang ada di dokumen berikut:\n\n" + context
)
    else:
        system_prompt = (
            "Kamu adalah pipin asisten pintarnya untuk menjawab pertanyaan user."
            "Jika user menanyakan tentang contoh screenshot, arahkan untuk melihat gambar yang tersedia."
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
        raise Exception(f"❌ Respon tidak valid dari OpenRouter:\n{result}")

    return result["choices"][0]["message"]["content"]

# === INPUT USER ===
user_input = st.text_input("❓ Pertanyaan kamu:", placeholder="Misal: Boleh uninstall aplikasinya?")

if user_input:
    st.chat_message("user").write(user_input)

    with st.spinner("Bot sedang mikir..."):
        try:
            response = ask_openrouter(user_input, mission_context)
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            st.session_state.chat_history.append({"role": "assistant", "content": response})
            st.chat_message("assistant").write(response)

            # === TAMPILKAN GAMBAR JIKA PERTANYAAN TENTANG SCREENSHOT ===
            screenshot_keywords = ["screenshot", "ss", "screen shot", "contoh gambar", "contoh tampilan"]
            if any(k in user_input.lower() for k in screenshot_keywords):
                image_path = "screenshots/contoh bener.jpeg"

                if os.path.exists(image_path):
                    with open(image_path, "rb") as img_file:
                        encoded = base64.b64encode(img_file.read()).decode()

                    st.markdown("---")
                    st.markdown(f"""
                        <div style='text-align:center;'>
                            <img src='data:image/jpeg;base64,{encoded}' width='200'/>
                            <p><em>📸 Contoh pengerjaan yang benar</em></p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                else:
                    st.warning("⚠️ Gambar tidak ditemukan. Pastikan file ada di folder 'screenshots/' dan bernama `contoh bener.jpeg`.")

        except Exception as e:
            st.error(str(e))
