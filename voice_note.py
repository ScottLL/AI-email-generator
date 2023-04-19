from googletrans import Translator, LANGUAGES
import datetime
import openai
from dotenv import load_dotenv
import openai
# load_dotenv()
import speech_recognition as sr

# Add the following imports
import io
import os
from google.cloud import speech_v1p1beta1 as speech
from google.oauth2 import service_account
import streamlit as st

import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase, ClientSettings
import requests



# Load dotenv
load_dotenv()

# Function to transcribe audio using Google Speech-to-Text API
def transcribe_audio(file_path: str, language: str, api_key: str) -> str:
    # Set Google Cloud credentials and API key
    credentials = service_account.Credentials.from_service_account_file(api_key)

    client = speech.SpeechClient(credentials=credentials)

    with io.open(file_path, "rb") as audio_file:
        content = audio_file.read()

    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code=language,
        enable_automatic_punctuation=True,
        model="default",
        use_enhanced=True,
    )

    response = client.recognize(config=config, audio=audio)

    transcription = ""
    for result in response.results:
        transcription += result.alternatives[0].transcript

    return transcription






def detect_language(text: str):
    translator = Translator()
    detected_language = translator.detect(text)
    return detected_language.lang

def translate(text: str, input_language: str, target_language: str, openai_api_key: str) -> str:
    # Add the following two lines
    
    openai.api_key = openai_api_key
    
    if input_language not in LANGUAGES.keys():
        input_language = detect_language(text)

    if input_language == target_language:
        return text

    translator = Translator()
    translation = translator.translate(text, src=input_language, dest=target_language)

    if translation:
        return translation.text
    else:
        return "Translation failed"


def save_conversation(conversation_history):
    filename = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".txt"
    with open(filename, "w") as f:
        for original_text, translated_text in conversation_history:
            f.write("Original Text:\n" + original_text + "\n")
            f.write("Translated Text:\n" + translated_text + "\n")
            f.write("\n")


def generate_summary(text: str, max_tokens: int = 300, openai_api_key=None) -> str:
    openai.api_key = openai_api_key
    prompt = f"Summarize the following conversation into bullet points, and make each bullet points in one line: {text} Summary:"
    message_log = [{"role": "user","content": prompt}]
    response = openai.ChatCompletion.create(
        model = "gpt-3.5-turbo",
        messages = message_log,
        max_tokens=max_tokens,
        stop=None,
        temperature=0.7,
    )
    
    for choice in response.choices:
        if "text" in choice:
            return choice.text

    text = response.choices[0].message.content
    return text
    
    
# def voice_note_app(openai_api_key):
#     st.title("Voice Note & Summarization")

#     st.markdown("#### Voice Recording")
#     st.write("Upload your voice recording here:")
#     uploaded_file = st.file_uploader("", type=["wav"])

#     st.markdown("#### Text Input")
#     input_text = st.text_area("Enter your text here:")

#     if st.button("Summarize"):
#         if uploaded_file is not None:
#             # Save the uploaded file to a temporary path and transcribe it
#             with open("temp.wav", "wb") as f:
#                 f.write(uploaded_file.getbuffer())
#             transcribed_text = transcribe_audio("temp.wav", "en-US", openai_api_key)
#             st.write("Transcribed Text:", transcribed_text)

#             # Combine transcribed text and input text
#             combined_text = transcribed_text + " " + input_text
#         else:
#             combined_text = input_text

#         summary = generate_summary(combined_text, max_tokens=300, api_key=openai_api_key)
#         st.write("Summary:", summary)


class AudioRecorder(VideoTransformerBase):
    def recv(self, frame):
        if frame.audio is not None:
            # Do something with the audio data, e.g., send it to your Flask app for processing
            # Here we're sending it as a WAV file
            response = requests.post(
                "http://localhost:5001/process_audio",
                files={"audio": ("audio.wav", frame.audio.to_wav())},
                headers={"openai_api_key": st.session_state.openai_api_key}
            )
            # Log the response from the Flask app
            st.write(response.json())


def voice_note_app(openai_api_key):
    st.header("Voice Note Recorder and Summarizer")
    webrtc_ctx = webrtc_streamer(
        key="voice-note-recorder",
        rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
        video_transformer_factory=AudioRecorder,
    )


