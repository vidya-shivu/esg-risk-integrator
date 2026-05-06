from flask import Blueprint, request, jsonify
from services.groq_client import generate_response
from services.security import sanitize_input, is_malicious

# Blueprint setup
generate_bp = Blueprint("generate", __name__)


def load_prompt(E, S, G):
    """
    Load prompt template from file and inject ESG values
    """
    with open("prompts/report_prompt.txt", "r", encoding="utf-8") as f:
        template = f.read()

    return template.format(E=E, S=S, G=G)


@generate_bp.route("/generate-report", methods=["POST"])
def generate_report():
    data = request.json or {}

    # Sanitize input
    E = sanitize_input(data.get("E"))
    S = sanitize_input(data.get("S"))
    G = sanitize_input(data.get("G"))

    # ESG numeric validation
    try:
        E = float(E)
        S = float(S)
        G = float(G)

        # Ensure ESG scores are within valid range
        if not all(0 <= v <= 100 for v in [E, S, G]):
            return jsonify({
                "error": "ESG scores must be between 0 and 100"
            }), 400

    except:
        return jsonify({
            "error": "Invalid ESG input"
        }), 400

    # Detect malicious prompt injection
    if any(is_malicious(str(v)) for v in [E, S, G]):
        return jsonify({
            "error": "Malicious input detected"
        }), 400

    # Build AI prompt
    prompt = load_prompt(E, S, G)

    # Generate AI response
    ai_response = generate_response(prompt)

    return jsonify({
        "data": ai_response,
        "generated_at": "now"
    })