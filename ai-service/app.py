from flask import Flask
from routes.describe import describe_bp
from routes.recommend import recommend_bp
from routes.report import report_bp

# ✅ Step 1: Create app FIRST
app = Flask(__name__)

# ✅ Step 2: Register all routes AFTER app is created
app.register_blueprint(describe_bp)
app.register_blueprint(recommend_bp)
app.register_blueprint(report_bp)

# ✅ Health check
@app.route('/health')
def health():
    return {"status": "ok"}

# ✅ Run server
if __name__ == '__main__':
    app.run(port=5000, debug=True)