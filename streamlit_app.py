import streamlit as st
import os
import requests
import base64
import zipfile
import io
from streamlit_searchbox import st_searchbox

# === Function untuk tanya ke OpenRouter ===
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
        "model": "deepseek/deepseek-r1:free",
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

# === Streamlit Config ===
st.set_page_config(page_title="Pipin Pintarnya", page_icon="🤖")

# Logo
with open("screenshots/Pipin.png", "rb") as image_file:
    logo_base64 = base64.b64encode(image_file.read()).decode()

st.markdown(f"""
<div style='display: flex; align-items: center; gap: 10px; margin-bottom: 10px;'>
    <img src='data:image/png;base64,{logo_base64}' width='100'/>
    <h1 style='margin: 0; font-size: 2.5rem;'>Pipin - Asisten Misi Pintar</h1>
</div>
""", unsafe_allow_html=True)

st.markdown("Tanya apa pun tentang misi yang tersedia. Pipin siap bantu jawab!")

# === Misi yang tersedia ===
missions_data = {
    "Traveloka": {"context_file": "misi_traveloka.txt"},
    "UOB": {"context_file": "misi_uob.txt"},
    "Rating & Review": {"context_file": None},
    "Customer Service": {"context_file": None}
}

# === AUTOSUGGEST ===
def search_mission(search_term: str):
    return [m for m in missions_data.keys() if search_term.lower() in m.lower()]

selected_mission = st_searchbox(
    search_function=search_mission,
    placeholder="🔍 Ketik nama misinya (misal: Traveloka)...",
    key="mission_search"
)

# === HANDLE MISI ===
if selected_mission:
    st.success(f"✅ Misi dipilih: {selected_mission}")

    if selected_mission == "Customer Service":
        st.markdown("### 💬 Riwayat Chat WhatsApp (Customer Service)")

        zip_url = "https://we.tl/t-fcrviTn9Ui"

        @st.cache_data(show_spinner=True)
        def load_zip_text_from_url(url):
            try:
                response = requests.get(url)
                if response.status_code != 200:
                    raise Exception("Gagal download file")

                with zipfile.ZipFile(io.BytesIO(response.content)) as z:
                    txt_files = [f for f in z.namelist() if f.endswith(".txt")]
                    if not txt_files:
                        raise Exception("Tidak ada file .txt dalam ZIP")
                    all_texts = ""
                    for fname in txt_files:
                        with z.open(fname) as f:
                            all_texts += f.read().decode("utf-8", errors="ignore") + "\n\n"
                    return all_texts
            except Exception as e:
                return f"❌ Gagal membaca ZIP: {e}"

        context = load_zip_text_from_url(zip_url)

        # Fallback: Upload file ZIP manual
        st.markdown("#### 🗂️ Atau upload ZIP chat WhatsApp (cadangan)")
        uploaded_zip = st.file_uploader("📎 Upload ZIP file:", type=["zip"])
        if uploaded_zip is not None:
            try:
                with zipfile.ZipFile(uploaded_zip) as z:
                    txt_files = [f for f in z.namelist() if f.endswith(".txt")]
                    all_texts = ""
                    for fname in txt_files:
                        with z.open(fname) as f:
                            all_texts += f.read().decode("utf-8", errors="ignore") + "\n\n"
                    context = all_texts
                    st.success("✅ ZIP berhasil dibaca dari upload manual.")
            except Exception as e:
                st.error(f"❌ Gagal baca ZIP upload: {e}")

        user_input = st.text_input("❓ Pertanyaan tentang isi chat:", placeholder="Misal: Ada komplain soal pesanan?")
        if user_input:
            st.chat_message("user").write(user_input)
            with st.spinner("Pipin lagi baca isi chat WA..."):
                try:
                    if context.startswith("❌"):
                        raise Exception(context)
                    response = ask_openrouter(user_input, context, "Customer Service")
                    st.chat_message("assistant").write(response)
                except Exception as e:
                    st.error(str(e))

    # Misimu lain? Lanjutkan sesuai versi kamu sebelumnya
    # ...
