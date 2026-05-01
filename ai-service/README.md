# 🌱 ESG AI Microservice

An AI-powered microservice that analyzes ESG (Environmental, Social, Governance) risks using LLM (Groq API).

---

# 🚀 Features

* ESG Risk Analysis (`/describe`)
* ESG Recommendations (`/recommend`)
* ESG Report Generation (`/generate-report`)
* Redis Caching (15 min TTL)
* Retry + Fallback Handling
* Secure API (input validation + headers)
* Health Monitoring (`/health`)

---

# ⚙️ Tech Stack

* Python (Flask)
* Groq API (LLM)
* Redis (Caching)
* JSON-based APIs

---

# 📦 Setup Instructions

## 1️⃣ Clone Repository

```bash
git clone https://github.com/vidya-shivu/esg-risk-integrator.git
cd esg-risk-integrator/ai-service
```

---

## 2️⃣ Create Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate   # Windows
```

---

## 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4️⃣ Setup Environment Variables

Create `.env` file:

```env
GROQ_API_KEY=your_api_key_here
```

---

## 5️⃣ Run Application

```bash
python app.py
```

Server will run on:

```bash
http://localhost:5000
```

---

# 🔍 API Endpoints

---

## 📌 1. Describe ESG Risk

### Endpoint:

```bash
POST /describe
```

### Request:

```json
{
  "text": "Company has high carbon emissions"
}
```

### Response:

```json
{
  "analysis": {
    "category": "Environmental",
    "severity": "High",
    "summary": "...",
    "impact": {
      "financial": "...",
      "legal": "...",
      "brand": "..."
    },
    "explanation": "..."
  },
  "source": "ai",
  "generated_at": "timestamp"
}
```

---

## 📌 2. Get Recommendations

### Endpoint:

```bash
POST /recommend
```

### Request:

```json
{
  "text": "Company has governance issues"
}
```

### Response:

```json
{
  "recommendations": [
    {
      "action_type": "Compliance",
      "description": "...",
      "priority": "High"
    }
  ],
  "source": "ai"
}
```

---

## 📌 3. Generate ESG Report

### Endpoint:

```bash
POST /generate-report
```

### Request:

```json
{
  "text": "Company has ESG risks"
}
```

### Response:

```json
{
  "title": "ESG Risk Report",
  "summary": "...",
  "overview": "...",
  "key_items": ["..."],
  "recommendations": [],
  "source": "ai",
  "generated_at": "timestamp"
}
```

---

# ⚠️ Fallback Response

If AI fails:

```json
{
  "is_fallback": true,
  "source": "fallback"
}
```

---

# ⚡ Performance

* Avg response time: ~1 second
* Redis caching enabled (15 min TTL)
* Retry mechanism implemented

---

# ❤️ Health Check

```bash
GET /health
```

Response:

```json
{
  "status": "ok",
  "uptime_seconds": 120,
  "avg_response_time_ms": 950
}
```

---

# 🔐 Security

* Input validation
* JSON enforcement
* Security headers (XSS, CSP, etc.)
* Safe error handling

---

# 📌 Notes

* Ensure Redis is running for caching
* If Redis is unavailable → system still works (fallback mode)

---

# 👨‍💻 Author

AI Developer Project — ESG Risk Integrator
