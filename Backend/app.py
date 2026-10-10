import os
import base64
from pathlib import Path

import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from google import genai

# Load API keys from the project root .env file
PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

app = Flask(__name__)
CORS(app)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MURF_API_KEY = os.getenv("MURF_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

MURF_URL = "https://global.api.murf.ai/v1/speech/stream"

VOICES = {
    "English": {"Male": "Matthew", "Female": "Alicia"},
    "Hindi": {"Male": "Aman", "Female": "Namrita"},
    "Tamil": {"Male": "Karthikeyan", "Female": "Anisha"},
    "Telugu": {"Male": "Zion", "Female": "Josie"},
}

LOCALES = {
    "English": "en-US",
    "Hindi": "hi-IN",
    "Tamil": "ta-IN",
    "Telugu": "te-IN",
}

SCRIPT_INSTRUCTIONS = {
    "English": "Write entirely in English using the Latin alphabet.",
    "Hindi": "Write entirely in Hindi using Devanagari script.",
    "Tamil": "Write entirely in Tamil using Tamil script.",
    "Telugu": (
        "Write entirely in Telugu using Telugu script (తెలుగు లిపి). "
        "Do not use Tamil script, Tamil words, or Latin transliteration. "
        "Use natural, grammatically correct Telugu."
    ),
}


@app.route("/generate-audio-guide", methods=["POST"])
def generate_audio_guide():
    data = request.get_json(silent=True) or {}

    place = data.get("place", "").strip()
    answer_type = data.get("answerType", "Summary")
    language = data.get("language", "English")
    voice_gender = data.get("voice", "Male")

    if not place:
        return jsonify({
            "error": "Please select a destination."
        }), 400

    if not GEMINI_API_KEY or not MURF_API_KEY:
        return jsonify({
            "error": "API keys are missing. Check your project .env file."
        }), 500

    if client is None:
        return jsonify({
            "error": "Gemini client is not configured."
        }), 500

    if language not in LOCALES or voice_gender not in ("Male", "Female"):
        return jsonify({
            "error": "Invalid language or voice selection."
        }), 400

    if answer_type not in ("Summary", "Detailed"):
        return jsonify({
            "error": "Invalid guide length."
        }), 400

    try:
        length_instruction = (
            "Write a short travel guide of about 100 words."
            if answer_type == "Summary"
            else "Write a detailed travel guide of about 350 words."
        )

        prompt = (
            f"Create an accurate, helpful travel guide about {place}. "
            f"The requested language is {language}. "
            f"{SCRIPT_INSTRUCTIONS[language]} "
            f"{length_instruction} "

            "Write fluent, natural, grammatically correct language "
            "that native speakers would comfortably understand. "

            "Use the correct writing system and spelling for the "
            "requested language. Do not mix languages unnecessarily. "
            "Do not produce corrupted words, random characters, "
            "incomplete sentences, or meaningless text. "

            "Include the place's history, important features, "
            "architecture or natural beauty, visitor tips, and "
            "reasons why people visit. "

            "Use simple, clear sentences that sound natural when "
            "spoken aloud. Organize the information logically and "
            "avoid unnecessary repetition. "

            "Use reliable, well-established facts. Do not invent "
            "historical events, dates, names, or visitor information. "
            "If an exact detail is uncertain, leave it out. "

            "Before responding, check the guide for spelling, grammar, "
            "clarity, factual consistency, and correct use of the "
            "requested language and writing system. "

            "Return only the travel guide, without a title, language "
            "label, translation, introductory note, or commentary. "
            "Keep the entire guide in the requested language."
        )

        # Generate the travel guide using Gemini
        gemini_response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt,
        )

        description = (gemini_response.text or "").strip()

        # Print the generated transcript in the backend terminal
        app.logger.info("Requested language: %s", language)
        app.logger.info("Gemini transcript: %s", description)

        if not description:
            return jsonify({
                "error": "Gemini returned an empty guide."
            }), 502

        # Prepare the Murf AI audio request
        murf_payload = {
            "voice_id": VOICES[language][voice_gender],
            "text": description,
            "locale": LOCALES[language],
            "model": "falcon-2",
            "format": "MP3",
            "sampleRate": 24000,
            "channelType": "MONO",
        }

        murf_response = requests.post(
            MURF_URL,
            headers={
                "api-key": MURF_API_KEY,
                "Content-Type": "application/json",
            },
            json=murf_payload,
            timeout=120,
        )

        if not murf_response.ok:
            app.logger.error(
                "Murf API error %s: %s",
                murf_response.status_code,
                murf_response.text[:500],
            )
            return jsonify({
                "error": (
                    "Murf could not generate the audio. "
                    "Check the backend terminal for details."
                )
            }), 502

        # Convert the generated audio to Base64 for the frontend
        audio_base64 = base64.b64encode(
            murf_response.content
        ).decode("utf-8")

        return jsonify({
            "description": description,
            "audioBase64": audio_base64,
        })

    except Exception:
        app.logger.exception("Audio guide generation failed")
        return jsonify({
            "error": (
                "The guide could not be generated. "
                "Check the backend terminal for details."
            )
        }), 500


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)

