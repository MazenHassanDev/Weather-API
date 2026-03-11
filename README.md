# Weather API

A Flask-based REST API that fetches weather data from [Visual Crossing](https://www.visualcrossing.com/weather-api) with Redis caching and rate limiting.

## How It Works

```
Request → Check Redis Cache → Cache Hit?
                                 ├── Yes → Return cached data (fast)
                                 └── No  → Call Visual Crossing API → Save to Redis → Return data
```

- Cache expiry: **12 hours** (data auto-deletes from Redis after 12h)
- Rate limit: **5 requests per minute** per IP on the weather endpoint
- Default limit: **100 requests per day / 10 per minute** across all endpoints

## Prerequisites

- Python 3.8+
- Redis server running locally ([download](https://github.com/microsoftarchive/redis/releases) for Windows)
- A free Visual Crossing API key ([get one here](https://www.visualcrossing.com/weather-api))

## Setup

**1. Clone the repo**
```bash
git clone https://github.com/MazenHassanDev/Weather-API.git
cd weather-api
```

**2. Create and activate a virtual environment**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Set up environment variables**
```bash
cp .env.example .env
```
Then open `.env` and fill in your API key and Redis URL.

**5. Make sure Redis is running**
```bash
redis-cli ping   # should return PONG
```

**6. Run the app**
```bash
python app.py
```

## API Endpoints

### Get Weather
```
GET /weather/<city>
```

**Example:**
```
GET http://localhost:5000/weather/london
```

**Response (first request — from API):**
```json
{
    "source": "api",
    "data": { ... }
}
```

**Response (subsequent requests — from cache):**
```json
{
    "source": "cache",
    "data": { ... },
    "cached": true,
    "expires_in_seconds": 43180,
    "expires_in_hours": 11.99
}
```

### Rate Limit Exceeded
```json
{
    "error": "Too many requests - slow down!",
    "message": "5 per 1 minute"
}
```

## Project Structure

```
weather-api/
├── app.py              # main Flask application
├── .env                # secret keys (not committed to git)
├── .env.example        # template for environment variables
├── .gitignore          # prevents secrets from being committed
├── requirements.txt    # Python dependencies
├── test_redis.py       # script to verify Redis connection
└── README.md           # this file
```

## Environment Variables

| Variable | Description |
|---|---|
| `WEATHER_API_KEY` | Your Visual Crossing API key |
| `REDIS_URL` | Redis connection URL (default: `redis://localhost:6379`) |
| `FLASK_KEY` | Secret key for Flask sessions |
