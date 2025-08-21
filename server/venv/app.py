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
Sources: Patch notes, pro-player guides, event FAQs, weapon stats
Focus: Sensitivity settings, weapon loadouts, character combos, spin probabilities
Player Context (if any): {player_context}
"""

        # ✅ System Prompt → Rules & boundaries
        system_prompt = """
You are BattleByte, an AI-powered Free Fire assistant.
- Only answer Free Fire-related queries.
- Be clear, factual, and concise.
- Avoid adding unrelated information.
"""

        # ✅ One-shot example (demonstration for the model)
        example_prompt = """
Example:
Player Query: "Which gun is best for close range in OB45?"
Answer: "The M1887 is the strongest close-range gun in OB45 due to its high damage. 
The MP40 is also reliable for faster spray. Both are popular rush choices."
"""

        # ✅ User Prompt → Actual player query with context
        user_prompt = f"""
Context:
{rag_context}

Player Query:
{query}
"""

        contents = [
            types.Content(role="model", parts=[types.Part(text=system_prompt)]),  # System
            types.Content(role="user", parts=[types.Part(text=user_prompt)])      # User
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
