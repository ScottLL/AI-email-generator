import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase, ClientSettings
import requests


class AudioRecorder(VideoTransformerBase):
    def recv(self, frame):
        if frame.audio is not None:
            # Do something with the audio data, e.g., send it to your Flask app for processing
            # Here we're sending it as a WAV file
            response = requests.post(
                "http://localhost:5001/process_audio",
                files={"audio": ("audio.wav", frame.audio.to_wav())},
            )
            # Log the response from the Flask app
            st.write(response.json())


def main():
    st.header("Audio Recorder and Summarizer")
    webrtc_ctx = webrtc_streamer(
        key="audio-recorder",
        mode=ClientSettings.RTC_ONLY,
        rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
        video_transformer_factory=AudioRecorder,
        in_local_storage_cursor=None,
        out_local_storage_cursor=None,
    )


# if __name__ == "__main__":
#     main()
