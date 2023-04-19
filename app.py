from werkzeug.utils import secure_filename
import os
from flask import  request, jsonify


UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"wav"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/process_audio", methods=["POST"])
def process_audio():
    if "audio" not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    audio = request.files["audio"]
    if audio.filename == "":
        return jsonify({"error": "No audio file provided"}), 400

    if audio and allowed_file(audio.filename):
        filename = secure_filename(audio.filename)
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        audio.save(file_path)
        openai_api_key = request.headers.get("openai_api_key")

        # Transcribe the audio and generate the summary
        transcribed_text = transcribe_audio(file_path, "en-US", openai_api_key)
        summary = generate_summary(transcribed_text, api_key=openai_api_key)

        return jsonify({"transcribed_text": transcribed_text, "summary": summary})
    else:
        return jsonify({"error": "Invalid file format"}), 400
