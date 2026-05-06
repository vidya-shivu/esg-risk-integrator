from flask import Blueprint, request, jsonify
from pathlib import Path
from services.groq_client import call_groq
from services.demo_metrics import track_demo_response
from utils.sanitizer import clean_input

import json
import re
import time
from datetime import datetime

recommend_bp = Blueprint("recommend", __name__)

@recommend_bp.route("/recommend", methods=["POST"])
def recommend():

    start_time = time.time()

    if not request.is_json:
        return jsonify({
            "error": "Request must be JSON"
        }), 400

    data = request.get_json()

    if not data:
        return jsonify({
            "error": "Request body is required"
        }), 400

    # ✅ Support BOTH formats
    if "text" in data:
        user_input = clean_input(data["text"]).strip()

    else:
        company = clean_input(data.get("company", ""))
        sector = clean_input(data.get("sector", ""))
        issue = clean_input(data.get("issue", ""))

        user_input = f"""
Company: {company}
Sector: {sector}
Issue: {issue}
""".strip()

    if not user_input:
        return jsonify({
            "error": "Empty input"
        }), 400

    print("INPUT:", user_input)

    prompt_template = Path("prompts/recommend_prompt.txt").read_text()

    prompt = prompt_template.replace("{input}", user_input)

    ai_response = call_groq(prompt)

    print("RAW AI:", ai_response)

    response_time = track_demo_response(start_time)

    # ✅ Fallback
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
            "is_fallback": True,
            "source": "fallback",
            "generated_at": datetime.utcnow().isoformat(),
            "response_time_seconds": response_time
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
        if not all(key in item for key in [
            "action_type",
            "description",
            "priority"
        ]):
            return jsonify({
                "error": "Invalid recommendation format",
                "raw": result
            }), 500

    return jsonify({
        "recommendations": result,
        "source": "ai",
        "generated_at": datetime.utcnow().isoformat(),
        "response_time_seconds": response_time,
        "is_fallback": False
    })