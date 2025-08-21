import os
from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # ✅ Enable CORS for all routes

# Initialize Gemini client
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

@app.route("/battlebyte", methods=["POST"])
def battlebyte():
    try:
        data = request.json
        query = data.get("query", "")
        player_context = data.get("player_context", "")

        rag_context = f"""
Game: Free Fire
Available info sources: Patch notes, pro-player guides, event FAQs, weapon stats
Focus: Sensitivity settings, weapon loadouts, character combos, spin probabilities
Player Context (if any): {player_context}
"""

        # ✅ Zero-shot prompt: No fixed persona, only task instruction
        task_prompt = f"""
Task: Answer Free Fire-related queries with accuracy using context below.
Be clear, factual, and avoid unrelated info.

Context:
{rag_context}

Player Query:
{query}
"""

        contents = [
            types.Content(role="user", parts=[types.Part(text=task_prompt)])
        ]

        def generate():
            try:
                for chunk in client.models.generate_content_stream(
                    model="gemini-2.0-flash",
                    contents=contents,
                    config=types.GenerateContentConfig(top_k=40)
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
