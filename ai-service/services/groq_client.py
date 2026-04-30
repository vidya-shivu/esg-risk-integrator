import os
import time
import hashlib
import redis
from groq import Groq
from dotenv import load_dotenv

# ✅ Load env
load_dotenv()

print("API KEY:", os.getenv("GROQ_API_KEY"))

# ✅ Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ✅ Track response times
response_times = []

# ✅ Redis setup
redis_client = redis.Redis(host='localhost', port=6379, db=0)

def call_groq(prompt, retries=2):

    # 🔐 Create cache key
    key = hashlib.sha256(prompt.encode()).hexdigest()

    # ✅ Check cache
    cached = redis_client.get(key)
    if cached:
        print("CACHE HIT")
        return cached.decode()

    for attempt in range(retries + 1):
        try:
            start = time.time()

            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )

            end = time.time()

            # ⏱️ Track response time (ms)
            response_times.append((end - start) * 1000)

            result = response.choices[0].message.content

            # ✅ Store in Redis (15 min TTL)
            redis_client.setex(key, 900, result)

            return result

        except Exception as e:
            print(f"Attempt {attempt+1} failed:", str(e))
            time.sleep(1)

    return None