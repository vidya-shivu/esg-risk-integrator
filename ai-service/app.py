from flask import Flask
from routes.describe import describe_bp
from routes.recommend import recommend_bp
from routes.report import report_bp
from services.groq_client import response_times
import time

# ✅ Track start time
start_time = time.time()

# ✅ Create app
app = Flask(__name__)

# ✅ Register routes
app.register_blueprint(describe_bp)
app.register_blueprint(recommend_bp)
app.register_blueprint(report_bp)

# ✅ Health endpoint (UPGRADED)
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

# ✅ Run server
if __name__ == '__main__':
    app.run(port=5000, debug=True)