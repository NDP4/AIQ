import streamlit as st
import requests
from dotenv import load_dotenv
import os
import datetime

# Load environment variables
load_dotenv()

# API Key dari .env
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
USERNAME_INTIP1 = os.getenv("USERNAME_INTIP1")
PASSWORD_INTIP1 = os.getenv("PASSWORD_INTIP1")
USERNAME_INTIP2 = os.getenv("USERNAME_INTIP2")
PASSWORD_INTIP2 = os.getenv("PASSWORD_INTIP2")

# URL endpoint untuk API Groq
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# Daftar model yang tersedia
MODELS = [
    {
        "id": "gemma-7b-it",
        "name": "Gemma 7B IT",
        "description": "Model dari Google dengan konteks window 8192."
    },
    {
        "id": "llama3-70b-8192",
        "name": "Llama 3 70B",
        "description": "Model dari Meta dengan konteks window 8,192."
    },
    {
        "id": "mixtral-8x7b-32768",
        "name": "Mixtral 8x7B",
        "description": "Model dari Mistral AI dengan konteks window 32768."
    }
]

# Fungsi untuk login
def login():
    st.session_state["username"] = st.text_input("Username", value="", placeholder="Masukkan username")
    password = st.text_input("Password", value="", type="password", placeholder="Masukkan password")

    if st.button("Login"):
        if (st.session_state["username"] == USERNAME_INTIP1 and password == PASSWORD_INTIP1) or \
           (st.session_state["username"] == USERNAME_INTIP2 and password == PASSWORD_INTIP2):
            st.session_state["authenticated"] = True
            st.session_state["model_id"] = None  # Reset model ID setelah login
            st.session_state["chat_history"] = []  # Reset chat history
        else:
            st.error("Login gagal. Username atau password salah.")

# Fungsi untuk memilih model
def select_model():
    st.sidebar.title("Pilih Model")

    model_options = [model["name"] for model in MODELS]
    selected_model_name = st.sidebar.selectbox("Pilih model", model_options)

    # Set model ID berdasarkan model yang dipilih
    selected_model = next(model for model in MODELS if model["name"] == selected_model_name)
    if st.sidebar.button("Setel Model"):
        st.session_state["model_id"] = selected_model["id"]
        st.sidebar.success(f"Model '{selected_model_name}' telah dipilih.")

# Fungsi untuk membuat AI Chat Interface
def ai_chat():
    st.title("AIQ - Groq AI")

    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []

    # Tempat untuk menampilkan chat history dan chat baru
    chat_container = st.empty()

    user_input = st.text_area("Masukkan pertanyaan Anda", "")

    if st.button("Kirim"):
        if user_input:
            model_id = st.session_state.get("model_id")
            if model_id:
                # Menggunakan API Groq secara langsung
                headers = {
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json"
                }
                payload = {
                    "model": model_id,
                    "messages": [{"role": "user", "content": user_input}],
                    "max_tokens": 1000,
                }
                response = requests.post(GROQ_API_URL, headers=headers, json=payload)
                if response.status_code == 200:
                    ai_response = response.json().get("choices", [{}])[0].get("message", {}).get("content", "Tidak ada respons dari API.")
                else:
                    ai_response = f"Error {response.status_code}: {response.text}"

                # Tambahkan chat ke history
                st.session_state["chat_history"].append({"user": user_input, "ai": ai_response})

                # Update chat container
                with chat_container.container():
                    st.markdown("<h3>Chat History:</h3>", unsafe_allow_html=True)
                    for chat in st.session_state["chat_history"]:
                        st.markdown(
                            f"""
                            <div style="display: flex; justify-content: flex-start; margin-bottom: 10px;">
                                <div style="background-color: #DCF8C6; border-radius: 10px; padding: 10px; max-width: 80%; word-wrap: break-word; color: #000000;">
                                    <strong>Anda:</strong> {chat['user']}
                                </div>
                            </div>
                            <div style="display: flex; justify-content: flex-end; margin-bottom: 10px;">
                                <div style="background-color: #FFFFFF; border-radius: 10px; padding: 10px; max-width: 80%; word-wrap: break-word; color: #000000;">
                                    <strong>AIQ:</strong> {chat['ai']}
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
            else:
                st.error("Model belum dipilih. Silakan pilih model di sidebar.")

    # Tampilkan chat history
    with chat_container.container():
        st.markdown("<h3>Chat History:</h3>", unsafe_allow_html=True)
        for chat in st.session_state["chat_history"]:
            st.markdown(
                f"""
                <div style="display: flex; justify-content: flex-start; margin-bottom: 10px;">
                    <div style="background-color: #DCF8C6; border-radius: 10px; padding: 10px; max-width: 80%; word-wrap: break-word; color: #000000;">
                        <strong>Anda:</strong> {chat['user']}
                    </div>
                </div>
                <div style="display: flex; justify-content: flex-end; margin-bottom: 10px;">
                    <div style="background-color: #FFFFFF; border-radius: 10px; padding: 10px; max-width: 80%; word-wrap: break-word; color: #000000;">
                        <strong>AIQ:</strong> {chat['ai']}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

    # Copyright Section
    current_year = datetime.now().year
    st.markdown(f"<p style='text-align: center; margin-top: 50px;'>© {current_year} Nur Dwi Priyambodo</p>", unsafe_allow_html=True)

# Main program
def main():
    st.sidebar.title("Login")

    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if not st.session_state["authenticated"]:
        login()
    else:
        select_model()
        st.sidebar.write(f"Selamat datang, {st.session_state['username']}")
        if st.sidebar.button("Logout"):
            st.session_state["authenticated"] = False
            st.session_state["username"] = ""
            st.session_state["model_id"] = None  # Reset model ID
            st.session_state["chat_history"] = []
            # Refresh page manually
            st.experimental_rerun()

        ai_chat()

if __name__ == "__main__":
    main()
