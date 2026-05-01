from flask import Blueprint, request, jsonify
from datetime import datetime
from pathlib import Path
from services.groq_client import call_groq
import json
import re
from utils.sanitizer import clean_input

describe_bp = Blueprint("describe", __name__)

@describe_bp.route("/describe", methods=["POST"])
def describe():

    # ✅ STEP 3: STRICT JSON VALIDATION
    if not request.is_json:
        return jsonify({
            "error": "Request must be JSON"
        }), 400

    data = request.get_json()

    # ✅ EXISTING VALIDATION (kept)
    if not data or "text" not in data:
        return jsonify({"error": "Missing 'text' field"}), 400

    # ✅ APPLY SANITIZATION HERE
    user_input = clean_input(data["text"]).strip()

    if not user_input:
        return jsonify({"error": "Empty input"}), 400

    print("INPUT:", user_input)

    # ✅ Load prompt
    prompt_template = Path("prompts/describe_prompt.txt").read_text()
    prompt = prompt_template.replace("{input}", user_input)

    # ✅ Call AI
    ai_response = call_groq(prompt)

    print("RAW AI:", ai_response)

    # ✅ Fallback
    if not ai_response:
        return jsonify({
            "analysis": {
                "category": "Unknown",
                "severity": "Medium",
                "summary": "Unable to analyze ESG risk at the moment.",
                "impact": {
                    "financial": "Potential financial implications require further review",
                    "legal": "Possible regulatory concerns",
                    "brand": "Reputational risks may exist"
                },
                "explanation": "Fallback response due to AI service unavailability"
            },
            "is_fallback": True,
            "source": "fallback",
            "generated_at": datetime.utcnow().isoformat()
        })

    # 🔥 FIXED JSON EXTRACTION (balanced braces method)
    try:
        start = ai_response.find("{")
        end = ai_response.rfind("}")

        if start == -1 or end == -1:
            raise ValueError("No JSON found")

        cleaned_json = ai_response[start:end+1]

        # Fix common AI issues
        cleaned_json = cleaned_json.replace(",}", "}").replace(",]", "]")

        result = json.loads(cleaned_json)

    except Exception as e:
        return jsonify({
            "error": "JSON parsing failed",
            "details": str(e),
            "raw": ai_response
        }), 500

    # ✅ Validate structure
    required_keys = ["category", "severity", "summary", "impact", "explanation"]

    if not all(key in result for key in required_keys):
        return jsonify({
            "error": "Invalid AI response format",
            "raw": result
        }), 500

    return jsonify({
        "analysis": result,
        "source": "ai",
        "generated_at": datetime.utcnow().isoformat()
    })