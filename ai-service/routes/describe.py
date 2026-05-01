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

    # ✅ APPLY SANITIZATION HERE (fixed placement)
    user_input = clean_input(data["text"]).strip()

    if not user_input:
        return jsonify({"error": "Empty input"}), 400

    print("INPUT:", user_input)

    # ✅ Load prompt (unchanged)
    prompt_template = Path("prompts/describe_prompt.txt").read_text()
    prompt = prompt_template.replace("{input}", user_input)

    # ✅ Call AI (unchanged)
    ai_response = call_groq(prompt)

    print("RAW AI:", ai_response)

    # ✅ Fallback (unchanged)
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
            "source": "fallback",
            "generated_at": datetime.utcnow().isoformat()
        })

    # ✅ Extract JSON (unchanged)
    match = re.search(r"\{.*\}", ai_response, re.DOTALL)

    if not match:
        return jsonify({
            "error": "No valid JSON object found",
            "raw": ai_response
        }), 500

    try:
        cleaned_json = match.group()

        # Fix common AI issues
        cleaned_json = cleaned_json.replace(",}", "}").replace(",]", "]")

        result = json.loads(cleaned_json)

    except Exception as e:
        return jsonify({
            "error": "JSON parsing failed",
            "details": str(e),
            "raw": ai_response
        }), 500

    # ✅ Validate structure (unchanged)
    required_keys = ["category", "severity", "summary", "impact", "explanation"]

    if not all(key in result for key in required_keys):
        return jsonify({
            "error": "Invalid AI response format",
            "raw": result
        }), 500

    # ✅ Final response (unchanged)
    return jsonify({
        "analysis": result,
        "source": "ai",
        "generated_at": datetime.utcnow().isoformat()
    })