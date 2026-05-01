from flask import Flask
from routes.describe import describe_bp
from routes.recommend import recommend_bp
from routes.report import report_bp
from services.groq_client import response_times
from datetime import datetime
import time

# ✅ Create app (ONLY ONCE)
app = Flask(__name__)

# ✅ Track start time
start_time = time.time()

# ✅ Security headers (ONLY ONE)
@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    return response

# ✅ Register routes
app.register_blueprint(describe_bp)
app.register_blueprint(recommend_bp)
app.register_blueprint(report_bp)

# ✅ Health endpoint
@app.route('/health')
def health():

    uptime = time.time() - start_time

    avg_time = 0
    if response_times:
        avg_time = sum(response_times) / len(response_times)

    return {
        "status": "ok",
        "model": "llama-3.1-8b-instant",
        "uptime_seconds": round(uptime, 2),
        "avg_response_time_ms": round(avg_time, 2)
    }

# ✅ Run server (FIXED)
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)