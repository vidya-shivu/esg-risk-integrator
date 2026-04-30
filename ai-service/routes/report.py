from flask import Blueprint, request, jsonify
from datetime import datetime
from pathlib import Path
from services.groq_client import call_groq
import json
import re

report_bp = Blueprint("report", __name__)

@report_bp.route("/generate-report", methods=["POST"])
def generate_report():

    data = request.get_json()

    # ✅ 1. Validate input
    if not data or "text" not in data:
        return jsonify({"error": "Missing 'text' field"}), 400

    user_input = data["text"].strip()

    if not user_input:
        return jsonify({"error": "Empty input"}), 400

    print("INPUT:", user_input)

    # ✅ 2. Load prompt
    prompt_template = Path("prompts/report_prompt.txt").read_text()
    prompt = prompt_template.replace("{input}", user_input)

    # ✅ 3. Call AI
    ai_response = call_groq(prompt)

    print("RAW AI:", ai_response)

    # ✅ 4. Fallback
    if not ai_response:
        return jsonify({
            "title": "ESG Risk Report",
            "summary": "Unable to generate report",
            "overview": "AI service unavailable",
            "key_items": ["Data unavailable"],
            "recommendations": [],
            "source": "fallback",
            "generated_at": datetime.utcnow().isoformat()
        })

    # ✅ 5. Extract JSON
    match = re.search(r"\{.*\}", ai_response, re.DOTALL)

    if not match:
        return jsonify({
            "error": "Invalid AI response",
            "raw": ai_response
        }), 500

    try:
        cleaned_json = match.group()
        cleaned_json = cleaned_json.replace(",}", "}").replace(",]", "]")

        result = json.loads(cleaned_json)

    except Exception as e:
        return jsonify({
            "error": "JSON parsing failed",
            "details": str(e),
            "raw": ai_response
        }), 500

    # ✅ 6. Validate structure
    required_keys = ["title", "summary", "overview", "key_items", "recommendations"]

    if not all(key in result for key in required_keys):
        return jsonify({
            "error": "Invalid report structure",
            "raw": result
        }), 500

    # ✅ 7. Final response
    return jsonify({
        **result,
        "source": "ai",
        "generated_at": datetime.utcnow().isoformat()
    })