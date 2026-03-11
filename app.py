import os
import json
import requests
import redis
from flask import Flask, jsonify, redirect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

app.secret_key = os.getenv("FLASK_KEY")

redis_client = redis.from_url(os.getenv('REDIS_URL'), decode_responses = True)

limiter = Limiter(get_remote_address, app=app, default_limits=['100 per day', '10 per minute'], storage_uri=os.getenv('REDIS_URL'))

API_KEY = os.getenv('WEATHER_API_KEY')
BASE_URL = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline"
CACHE_EXPIRY_SECONDS = 12 * 60 * 60

def fetch_from_weather_api(city):
    url = f"{BASE_URL}/{city}"
    params = {
        "unitGroup" : "metric",
        "key" : API_KEY,
        "contentType" : "json",
        "include" : "current"
    }

    response = requests.get(url, params=params, timeout=10)

    response.raise_for_status()

    return response.json()

@app.route('/')
def home():
    return redirect('/weather/london')

@app.route('/weather/<city>', methods=['GET'])
@limiter.limit('5 per minute')
def get_weather(city):
    
    city_key = city.lower().strip()

    cached = redis_client.get(city_key)


    if cached:
        ttl = redis_client.ttl(city_key)
        return jsonify({
            "source" : "cache",
            "data" : json.loads(cached),
            "cached" : True,
            "expires_in_seconds" : ttl,
            "expires_in_hours" : round(ttl / 3600, 2)
        }), 200
    
    try:
        weather_data = fetch_from_weather_api(city_key)
    
    except requests.exceptions.HTTPError as e:
        status = e.response.status_code
        if status == 400:
            return jsonify({"error" : f"City '{city}' not found."}), 404
        elif status == 401:
            return jsonify({"error" : "Invalid API key."}), 500
        else:
            return jsonify({"error" : "Weather service error."}), 502
    
    except requests.exceptions.ConnectionError:
        return jsonify({"error" : "Could not reach weather service." }), 503
    
    except requests.exceptions.Timeout:
        return jsonify({"error": "Request timed out."}), 504
    
    redis_client.set(city_key, json.dumps(weather_data), ex=CACHE_EXPIRY_SECONDS)

    return jsonify({
        "source" : "api",
        "data" : weather_data
    }), 200

@app.errorhandler(429)
def rate_limit_reached(e):
    return jsonify({
        "error" : "Too many requests - slow down!",
        "message" : str(e.description)
    }), 429

if __name__ == "__main__":
    app.run(debug=True)