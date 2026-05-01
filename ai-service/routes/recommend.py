from flask import Blueprint, request, jsonify
from pathlib import Path
from services.groq_client import call_groq
import json
import re
from utils.sanitizer import clean_input

recommend_bp = Blueprint("recommend", __name__)

@recommend_bp.route("/recommend", methods=["POST"])
def recommend():

    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()

    if not data or "text" not in data:
        return jsonify({"error": "Missing 'text' field"}), 400

    user_input = clean_input(data["text"]).strip()

    if not user_input:
        return jsonify({"error": "Empty input"}), 400

    print("INPUT:", user_input)

    prompt_template = Path("prompts/recommend_prompt.txt").read_text()
    prompt = prompt_template.replace("{input}", user_input)

    ai_response = call_groq(prompt)

    print("RAW AI:", ai_response)

    # ✅ Fallback (UPDATED)
    if not ai_response:
        return jsonify({
            "recommendations": [
                {
                    "action_type": "Compliance",
                    "description": "Ensure adherence to ESG regulations and conduct audits",
                    "priority": "High"
                },
                {
                    "action_type": "Operational",
                    "description": "Implement internal monitoring systems for ESG risks",
                    "priority": "Medium"
                },
                {
                    "action_type": "Strategic",
                    "description": "Develop long-term ESG governance strategy",
                    "priority": "High"
                }
            ],
            "is_fallback": True,   # 🔥 ADDED
            "source": "fallback"
        })

    match = re.search(r"\[.*\]", ai_response, re.DOTALL)

    if not match:
        return jsonify({
            "error": "No valid JSON array found",
            "raw": ai_response
        }), 500

    try:
        cleaned_json = match.group()
        cleaned_json = cleaned_json.replace(",]", "]")
        result = json.loads(cleaned_json)

    except Exception as e:
        return jsonify({
            "error": "JSON parsing failed",
            "details": str(e),
            "raw": ai_response
        }), 500

    if not isinstance(result, list) or len(result) != 3:
        return jsonify({
            "error": "AI did not return exactly 3 recommendations",
            "raw": result
        }), 500

    for item in result:
        if not all(key in item for key in ["action_type", "description", "priority"]):
            return jsonify({
                "error": "Invalid recommendation format",
                "raw": result
            }), 500

    return jsonify({
        "recommendations": result,
        "source": "ai"
    })