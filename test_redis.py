import redis
import os
from dotenv import load_dotenv

load_dotenv()

client = redis.from_url(os.getenv("REDIS_URL"), decode_responses=True)

try:
    client.ping()
    print("Redis connected successfully!")

    # Test set and get
    client.set("test_key", "hello from flask!", ex=60)
    value = client.get("test_key")
    print(f"Test value set and retrieved: {value}")

except redis.exceptions.ConnectionError as e:
    print(f"ERROR: Could not connect to Redis: {e}")