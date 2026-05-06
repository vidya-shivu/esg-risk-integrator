from flask import Flask
from routes.describe import describe_bp
from routes.recommend import recommend_bp
from routes.report import report_bp

from services.groq_client import response_times
from services.demo_metrics import get_average_response_time

from datetime import datetime
from werkzeug.serving import WSGIRequestHandler

import time

# ✅ Hide Werkzeug version
WSGIRequestHandler.server_version = "SecureServer"
WSGIRequestHandler.sys_version = ""

# ✅ Create Flask app
app = Flask(__name__)

# ✅ App startup time
start_time = time.time()

# ==============================
# SECURITY HEADERS
# ==============================

@app.after_request
def add_security_headers(response):

    response.headers["X-Content-Type-Options"] = "nosniff"

    response.headers["X-Frame-Options"] = "DENY"

    response.headers["X-XSS-Protection"] = "1; mode=block"

    response.headers["Strict-Transport-Security"] = (
        "max-age=31536000; includeSubDomains"
    )

    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self'; "
        "style-src 'self'; "
        "img-src 'self' data:; "
        "font-src 'self'; "
        "connect-src 'self'; "
        "object-src 'none'; "
        "base-uri 'self'; "
        "form-action 'self';"
    )

    # ✅ Hide server info
    response.headers["Server"] = "SecureServer"

    return response

# ==============================
# REGISTER ROUTES
# ==============================

app.register_blueprint(describe_bp)
app.register_blueprint(recommend_bp)
app.register_blueprint(report_bp)

# ==============================
# HEALTH ENDPOINT
# ==============================

@app.route("/health")
def health():

    uptime = round(time.time() - start_time, 2)

    avg_response_time = get_average_response_time()

    # ✅ Optional Groq timing fallback
    groq_avg = 0

    if response_times:
        groq_avg = round(
            sum(response_times) / len(response_times),
            2
        )

        # ✅ Memory optimization
        if len(response_times) > 50:
            response_times.pop(0)

    return {
        "status": "healthy",
        "api_version": "1.0",
        "timestamp": datetime.utcnow().isoformat(),

        "uptime_seconds": uptime,

        "average_response_time_seconds": avg_response_time,

        "groq_average_response_time_seconds": groq_avg,

        "services": {
            "redis": "connected",
            "chromadb": "connected",
            "groq_model": "llama-3.1-8b-instant"
        }
    }

# ==============================
# ERROR HANDLING
# ==============================

@app.errorhandler(500)
def handle_500_error(e):

    return {
        "error": "Internal server error"
    }, 500

# ==============================
# RUN APPLICATION
# ==============================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )
from routes.generate import generate_bp
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)

# Global rate limiter
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["30 per minute"]
)

# Register blueprint
app.register_blueprint(generate_bp)


@app.route("/")
def home():
    return "AI Service Running"


if __name__ == "__main__":
    app.run(debug=True, port=5000)
