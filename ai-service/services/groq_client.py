import os
import time
import hashlib
import redis
from groq import Groq
from dotenv import load_dotenv

# ✅ Load env
load_dotenv()

# ✅ Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ✅ Track response times
response_times = []

# ✅ Redis setup
redis_client = redis.Redis(host='localhost', port=6379, db=0)

def call_groq(prompt, retries=2):

    start = time.time()

    # 🔐 Cache key
    key = hashlib.sha256(prompt.encode()).hexdigest()

    # ✅ Safe cache (no crash if Redis down)
    try:
        cached = redis_client.get(key)
        if cached:
            print("CACHE HIT")
            return cached.decode()
    except Exception:
        pass

    for attempt in range(retries + 1):
        try:
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500   # ✅ Faster response
            )

            result = response.choices[0].message.content

            end = time.time()

            # ⏱ Track response time
            elapsed = (end - start) * 1000
            response_times.append(elapsed)

            # 🔒 Limit memory (important)
            if len(response_times) > 50:
                response_times.pop(0)

            # ✅ Safe Redis store
            try:
                redis_client.setex(key, 900, result)
            except Exception:
                pass

            return result

        except Exception as e:
            print(f"Attempt {attempt+1} failed")

            if attempt == retries:
                return None   # 🚨 triggers fallback

            time.sleep(1)