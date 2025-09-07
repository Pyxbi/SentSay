from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests
import json
from typing import List, Dict

from config import FIREWORKS_API_KEY, FIREWORKS_API_URL, FIREWORKS_MODEL, PORT, DEBUG

app = Flask(__name__)
CORS(app)


def build_system_prompt() -> str:
    return (
        "You are SentSay, an assistant that crafts concise, emotionally intelligent replies to real-life messages. "
        "Optimize for clarity, warmth, and natural texting tone. Keep messages short, sound human, and avoid emojis unless explicitly asked."
    )


def build_tone_guidance(tone: str) -> str:
    tone_map: Dict[str, str] = {
        "confident": "Direct, certain, and clear. No hedging. Friendly but assertive.",
        "kind": "Warm, gentle, supportive. Use softening language and kindness.",
        "flirty": "Playful, charming, light. Subtle confidence. Keep it tasteful.",
        "professional": "Polished, courteous, and concise. Appropriate for work contexts.",
        "gen z": "Casual, trend-aware, light slang ok. Keep it short and real.",
    }
    return tone_map.get(tone.lower(), "Neutral, helpful, and concise.")

# instruction
def build_instruction(situation: str, tone: str, tone_guidance: str) -> str:
    # Check for the keyword "email" in the situation text
    if 'email' in situation.lower():
        # Return a special instruction for formatting emails
        return (
            f"Write a complete email based on the user's message in a '{tone}' tone. "
            f"Tone guidance: {tone_guidance}. "
            f"Context/situation: {situation}. "
            "The output must be a single string in proper email format, including 'Subject:' and a sign-off. "
            "Return a raw JSON array containing this one email string. Example format: [\"Subject: Following Up\\n\\nHi [Name],\\n\\n...\"]"
        )
    
    # Default instruction for texting, DMs, etc.
    return (
        f"Rewrite the user's message in the '{tone}' tone for a texting conversation. "
        f"Tone guidance: {tone_guidance} "
        f"Context/situation: {situation or 'general texting'}. "
        "Return a raw JSON array of 3 short, copy-ready strings. Example format: [\"Option 1\", \"Option 2\", \"Option 3\"]"
    )


@app.route('/api/generate', methods=['POST'])
def generate():
    data = request.get_json(force=True) or {}
    user_message: str = data.get('message', '').strip()
    situation: str = data.get('situation', '').strip()
    tone: str = data.get('tone', 'Confident')

    if not FIREWORKS_API_KEY:
        return jsonify({"error": "Server misconfigured: missing FIREWORKS_API_KEY"}), 500
    if not user_message:
        return jsonify({"error": "message is required"}), 400

    system_prompt = build_system_prompt()
    tone_guidance = build_tone_guidance(tone)
    
    # Use our new dynamic instruction builder
    instruction = build_instruction(situation, tone, tone_guidance)

    payload = {
        "model": FIREWORKS_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"User message: {user_message}\nInstruction: {instruction}"},
        ],
        "temperature": 0.7,
        # Increase max_tokens for longer formats like email
        "max_tokens": 512, 
        "presence_penalty": 0.0,
        "frequency_penalty": 0.2,
    }

    headers = {
        "Authorization": f"Bearer {FIREWORKS_API_KEY}",
        "Content-Type": "application/json",
    }

    try:
        fw_res = requests.post(FIREWORKS_API_URL, json=payload, headers=headers, timeout=30)
        fw_res.raise_for_status()
        data = fw_res.json()
        content = data.get('choices', [{}])[0].get('message', {}).get('content', '')
        
        options: List[str] = json.loads(content)
        
        return jsonify({"options": options, "raw": content})
    except json.JSONDecodeError:
        options = [o.strip() for o in content.split('\n') if o.strip()]
        return jsonify({"options": options, "raw": content})
    except requests.HTTPError as e:
        return jsonify({"error": "Upstream error", "details": str(e), "body": getattr(e.response, 'text', '')}), 502
    except Exception as e:
        return jsonify({"error": "Server error", "details": str(e)}), 500


@app.route('/')
def index():
    return send_from_directory('static', 'index.html')


@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT, debug=DEBUG)
