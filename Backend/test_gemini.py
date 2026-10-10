
import os
from pathlib import Path
from dotenv import load_dotenv
from google import genai

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

response = client.models.generate_content(
    model="gemini-3.6-flash",
    contents="Reply with exactly this Telugu word and nothing else: నమస్కారం",
)

print("\n--- GEMINI TELUGU TEST ---\n")
print("Raw output:", repr(response.text))
