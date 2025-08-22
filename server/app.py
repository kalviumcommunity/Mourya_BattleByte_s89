import os
import re
from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize Gemini client
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

# ---------- Custom, exact answers ----------

CREATOR_SHORT = "Kadali Mourya."
MOURYA_BIO_SHORT = (
    
    "Kadali Mourya is currently studying at Godavari Global University, "
    "pursuing a B.Tech in Software Product Engineering (Kalvium)."
    "He is the creator of BattleByte, an AI-powered Free Fire assistant."




)

FREEFIRE_CREATOR_SHORT = "Free Fire was created by 111dots Studio and published by Garena."

def normalize(s: str) -> str:
    return (s or "").strip().lower()

def match_any(text: str, patterns) -> bool:
    return any(re.search(p, text) for p in patterns)

def handle_custom_intents(query: str):
    """
    Returns (handled: bool, response_text: str)
    """
    q = normalize(query)

    # Who created/made BattleByte (or you)
    if match_any(q, [
        r"\bwho\s+created\s+(you|battlebyte)\b",
        r"\bwho\s+made\s+(you|battlebyte)\b",
        r"\bwho\s+invented\s+(you|battlebyte)\b",
        r"\bwho\s+is\s+the\s+creator\s+of\s+(you|battlebyte)\b",
        r"\bwho\s+built\s+(you|battlebyte)\b",
        r"\bcreator\s+of\s+(you|battlebyte)\b",
        r"\bwho\s+developed\s+(you|battlebyte)\b"
    ]):
        return True, CREATOR_SHORT

    # Tell about Mourya
    if match_any(q, [
        r"\btell\s+about\s+mourya\b",
        r"\bwho\s+is\s+mourya\b",
        r"\bkadali\s+mourya\b",
        r"\babout\s+mourya\b"
    ]):
        return True, MOURYA_BIO_SHORT

    # Free Fire: who created / when created
    if match_any(q, [
        r"\bwho\s+created\s+free\s*fire\b",
        r"\bwho\s+made\s+free\s*fire\b",
        r"\bwho\s+developed\s+free\s*fire\b",
        r"\bwhen\s+was\s+free\s*fire\s+created\b",
        r"\bwhen\s+was\s+free\s*fire\s+released\b"
    ]):
        return True, FREEFIRE_CREATOR_SHORT

    return False, ""

# ---------- Route ----------

@app.route("/battlebyte", methods=["POST"])
def battlebyte():
    try:
        data = request.json or {}
        query = data.get("query", "")
        player_context = data.get("player_context", "")
        player_level = data.get("player_level", "Beginner")
        current_event = data.get("current_event", "None")

        # 1) Custom intents (exact answers first)
        handled, custom_text = handle_custom_intents(query)
        if handled:
            return Response(custom_text, mimetype="text/plain")

        # 2) Otherwise → Gemini fallback (Free Fire only)
        """
                    config=types.GenerateContentConfig(
                        top_k=40,
                        temperature=0.2,
                        max_output_tokens=200  # keep it short
                    )
                ):
                    if chunk.text:
                        yield chunk.text
            except Exception as e:
                yield f"[ERROR] {str(e)}"

        return Response(stream_with_context(generate()), mimetype="text/plain")

    except Exception as e:
        print("Error:", e)
        return jsonify({"answer": "", "error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, threaded=True)
