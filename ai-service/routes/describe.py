from flask import Blueprint, request, jsonify
from datetime import datetime
from pathlib import Path
from services.groq_client import call_groq
from services.chroma_service import search_esg_knowledge
from services.demo_metrics import track_demo_response
from utils.sanitizer import clean_input

import json
import time

describe_bp = Blueprint("describe", __name__)

@describe_bp.route("/describe", methods=["POST"])
def describe():

    start_time = time.time()

    # ✅ Validate JSON request
    if not request.is_json:
        return jsonify({
            "error": "Request must be JSON"
        }), 400

    data = request.get_json()

    # ✅ Validate request body
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

    # ✅ Empty validation
    if not user_input:
        return jsonify({
            "error": "Empty input"
        }), 400

    print("INPUT:", user_input)

    # ✅ Load prompt
    prompt_template = Path("prompts/describe_prompt.txt").read_text()

    # ✅ ChromaDB retrieval
    knowledge = search_esg_knowledge(user_input)

    context = "\n".join(knowledge)

    enhanced_input = f"""
User Input:
{user_input}

Relevant ESG Knowledge:
{context}
"""

    prompt = prompt_template.replace("{input}", enhanced_input)

    # ✅ Call Groq
    ai_response = call_groq(prompt)

    print("RAW AI:", ai_response)

    response_time = track_demo_response(start_time)

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
            "generated_at": datetime.utcnow().isoformat(),
            "response_time_seconds": response_time
        })

    # ✅ Extract JSON
    try:
        start = ai_response.find("{")
        end = ai_response.rfind("}")

        if start == -1 or end == -1:
            raise ValueError("No JSON found")

        cleaned_json = ai_response[start:end + 1]

        cleaned_json = cleaned_json.replace(",}", "}").replace(",]", "]")

        result = json.loads(cleaned_json)

    except Exception as e:
        return jsonify({
            "error": "JSON parsing failed",
            "details": str(e),
            "raw": ai_response
        }), 500

    # ✅ Validate AI response
    required_keys = [
        "category",
        "severity",
        "summary",
        "impact",
        "explanation"
    ]

    if not all(key in result for key in required_keys):
        return jsonify({
            "error": "Invalid AI response format",
            "raw": result
        }), 500

    return jsonify({
        "analysis": result,
        "source": "ai",
        "generated_at": datetime.utcnow().isoformat(),
        "response_time_seconds": response_time,
        "is_fallback": False
    })