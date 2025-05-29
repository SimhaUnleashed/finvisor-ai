import streamlit as st
import requests
import time
import streamlit.components.v1 as components
import assemblyai as aai
import speech_recognition as sr
import os
from dotenv import load_dotenv
load_dotenv()

api_url = os.getenv("API_URL", "http://localhost:8000")

# Configure Streamlit
st.set_page_config(page_title="Finance Chatbot", page_icon="🧠")
st.title("Finance Chatbot")
st.caption("Ask finance questions via voice or text.")

# Hide Streamlit UI elements
st.markdown("""
<style>
    [data-testid="stToolbar"], footer, .embeddedAppMetaInfoBar_container__DxxL1 {
        visibility: hidden !important;
    }

    .fixed-input {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: white;
        padding: 10px 1rem 0.5rem 1rem;
        box-shadow: 0 -2px 8px rgba(0,0,0,0.1);
        z-index: 999;
    }

    .block-container {
        padding-bottom: 130px !important; /* Space above fixed input */
    }
</style>
""", unsafe_allow_html=True)

# Setup TTS
def speak(text):
    escaped = text.replace('"', r'\"')
    js = f"""
    <script>
    var msg = new SpeechSynthesisUtterance("{escaped}");
    window.speechSynthesis.speak(msg);
    </script>
    """
    components.html(js, height=0)

# Initialize session state
if "history" not in st.session_state:
    st.session_state.history = []

# Voice input handler
def get_voice_input():
    aai.settings.api_key = os.getenv("ASSEMBLYAI_API_KEY")

    if not aai.settings.api_key:
        st.error("AssemblyAI API key not found. Please set the 'ASSEMBLYAI_API_KEY' environment variable or use Streamlit secrets.")
        return None

    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        with st.spinner("🎤 Listening..."):
            try:
                # Wait indefinitely for phrase start, record max 15 seconds
                # We'll save the audio to a temporary file for AssemblyAI to process.
                audio = recognizer.listen(source, timeout=None, phrase_time_limit=15)
                audio_file_path = "temp_audio.wav"
                with open(audio_file_path, "wb") as f:
                    f.write(audio.get_wav_data())

                st.spinner("🗣️ Transcribing with AssemblyAI...")
                # Transcribe the local audio file using AssemblyAI
                config = aai.TranscriptionConfig(speech_model=aai.SpeechModel.best)

                transcript = aai.Transcriber(config=config).transcribe(audio_file_path)

                # Clean up the temporary audio file
                os.remove(audio_file_path)

                if transcript.text:
                    return transcript.text
                else:
                    st.warning("AssemblyAI could not transcribe any speech.")
                    return None
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")
                return None

# Display chat history
for role, msg in st.session_state.history:
    with st.chat_message(role):
        st.markdown(msg)

# Sidebar button
with st.sidebar:
    if st.button("Clear Chat Window", use_container_width=True):
        st.session_state.history = []
        st.rerun()

# Fixed input section
# components.html('<div class="fixed-input" id="chat-input-anchor"></div>', height=0)
input_container = st.container()
with input_container:
    col1, col2 = st.columns([8, 2])
    with col1:
        prompt = st.chat_input("Type your question...")
    with col2:
        if st.button("🎙️ Speak", use_container_width=True):
            prompt = get_voice_input()

# Send prompt and handle stream
if prompt:
    st.session_state.history.append(("user", prompt))
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        try:
            with requests.post(
                f"{api_url}/v1/agents/finance_agent/runs",
                json={"message": prompt},
                stream=True,
                timeout=30,
            ) as res:
                res.raise_for_status()
                for chunk in res.iter_content(chunk_size=32):
                    if chunk:
                        decoded = chunk.decode("utf-8")
                        full_response += decoded
                        message_placeholder.markdown(full_response + "_")
                        time.sleep(0.02)
        except Exception as e:
            message_placeholder.markdown(f"Error: {e}")
            st.session_state.history.append(("assistant", f"Error: {e}"))
        else:
            message_placeholder.markdown(full_response)
            st.session_state.history.append(("assistant", full_response))
            speak(full_response)
