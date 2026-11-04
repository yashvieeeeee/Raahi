# 🚌 Raahi - Smart Commuting Assistant

![Python](https://img.shields.io/badge/Python-3.12-blue)
![Flask](https://img.shields.io/badge/Flask-3.0.3-black)
![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-336791)
![Vercel](https://img.shields.io/badge/Deploy-Vercel-black)

Smart Commuting Intelligence for Safer, Cleaner, and Better Daily Travel

An intelligent commuting assistant that helps users optimize their public transportation journey with real-time air quality data, fare predictions, and route recommendations. Built with Flask, PostgreSQL, and machine learning models.

Live app: `https://raahi-wine.vercel.app`

## Why Raahi Exists

Daily commuters make small travel decisions every day: which route to take, whether to walk, take a train, use a bus, or choose an auto. Those choices affect time, money, comfort, and emissions.

Raahi exists to make those choices easier. Instead of showing raw data, it turns route, fare, AQI, and trip information into simple commuting insights.

The goal is simple: help people travel smarter without needing to understand maps APIs, air-quality systems, or ML models.

## What Raahi Does

### For Commuters

| Feature | What It Does | Why It Matters |
| --- | --- | --- |
| Route Planner | Compares walking, train, bus, and auto options for a destination. | Helps users choose the best route for time, cost, and emissions. |
| AQI Awareness | Shows air-quality context for commuting decisions. | Helps users understand pollution exposure before travelling. |
| Trip Tracking | Saves completed trips with distance, cost, and CO2 details. | Builds a personal commuting history. |
| Profile Dashboard | Shows trips taken, CO2 saved, and money saved. | Makes sustainable travel progress visible. |
| Location Support | Uses saved user location for route planning. | Makes future route searches faster and more personal. |

### For Admins

| Feature | What It Does | Why It Matters |
| --- | --- | --- |
| Admin Dashboard | Displays users, trips, AQI summaries, and route activity. | Gives a quick overview of platform usage. |
| User Management | Lists and manages registered users. | Keeps the system easier to monitor. |
| Analytics Export | Prepares structured analytics data. | Supports reporting and review. |
| Model Metrics | Shows available ML/model health information where supported. | Keeps optional ML features transparent. |

## Project Refinements

### 1. Cleaner Commuter Experience

Raahi keeps the commuter flow simple: enter a destination, compare travel options, and understand the tradeoffs. The interface avoids technical language and focuses on practical outputs like time, fare, CO2 impact, and AQI context.

### 2. AQI-Aware Route Planning

Route suggestions are not only about speed. Raahi adds air-quality awareness so users can think about exposure, sustainability, and comfort while choosing how to travel.

### 3. Personal Impact Tracking

The profile dashboard turns saved trips into useful feedback. Users can see trips taken, money saved, and CO2 saved, making daily commute choices feel measurable instead of invisible.

### 4. Admin Intelligence Dashboard

Admins get a higher-level view of users, trips, route activity, AQI summaries, and optional model metrics. This makes Raahi easier to monitor as a working mobility platform rather than just a route form.

### 5. Lightweight Serverless Build

Vercel serverless functions have strict bundle limits, so production dependencies are kept lightweight. Heavy ML packages are treated as optional and are better suited for local development or a separate ML service.

## Technical Features

### Flask Backend

Built with Flask, Flask-Login, and Flask-SQLAlchemy. The backend is organized into focused route modules for authentication, web pages, APIs, admin tools, and optional ML endpoints.

### PostgreSQL Data Layer

Uses SQLAlchemy models for users and trips. Local development can run PostgreSQL through Docker, while production uses an externally reachable cloud database URL.

### Route and Fare Intelligence

Raahi estimates route distance, travel time, fare, and CO2 impact across multiple commute modes. This helps users compare options without switching between different tools.

### Air Quality Integration

AQI data is used to add environmental context to commuting decisions. The app is designed to support external air-quality providers such as WAQI and OpenAQ.

### Admin Analytics

The admin layer summarizes user activity, trip counts, route usage, AQI patterns, and model availability. It gives maintainers a compact view of how the platform is being used.

### Optional ML Advisory Layer

The `raahi_ml/` folder contains optional model pipelines and helpers. These are useful for local experimentation, but are not part of the lightweight Vercel production bundle.

## Project Structure

```text
backend/      Flask routes, services, database models
frontend/     Jinja templates, CSS, JavaScript, images
raahi_ml/     Optional ML pipelines and model helpers
config/       App settings
scripts/      Utility and database scripts
tests/        Test files
```

## Configuration & Environment Variables

Raahi reads all runtime settings from environment variables (or a local `.env` / `.env.local` file). A template is available in [`.env.example`](.env.example).

### Required & Optional Variables

| Variable | Requirement | Default / Fallback | Description & Security Notes |
| :--- | :--- | :--- | :--- |
| `SECRET_KEY` | **Required (Prod)** | Dev warning in debug | Session encryption secret. Must be a secure random 32+ byte hex string. The app raises a fatal `RuntimeError` at startup in production if unset or default. Generate with `python -c "import secrets; print(secrets.token_hex(32))"`. |
| `DATABASE_URL` | **Required (Prod)** | SQLite (`instance/raahi.db`) | PostgreSQL connection URI (`postgresql://user:pass@host:5432/dbname`). Automatically normalizes legacy `postgres://` schemes and enables connection pool pre-pinging. **Mandatory in production** as serverless environments (e.g. Vercel) have read-only filesystems. |
| `ADMIN_EMAIL` | **Required** | `admin@raahi.local` | Email address reserved for admin dashboard sign-in. Blocked from public registration. |
| `ADMIN_PASSWORD` | **Required** | None (disabled) | High-entropy password for admin dashboard access. Admin authentication is strictly disabled if this variable is empty or unset. |
| `WAQI_API_TOKEN` | Optional | Regional fallback | World Air Quality Index API token for live Mumbai air quality monitoring. Get a free token at [aqicn.org/api](https://aqicn.org/api/). Falls back gracefully to cached sensor snapshots if omitted. |
| `GOOGLE_MAPS_API_KEY` | Optional | OSRM + Presets | Google Maps Directions & Geocoding API key. If omitted or quota-denied (`REQUEST_DENIED`), automatically falls back to OSRM routing and Mumbai landmark presets without crashing. |
| `RATELIMIT_STORAGE_URI` | Optional | `memory://` | Storage backend for `Flask-Limiter`. Defaults to in-memory tracking. Set to `redis://...` for distributed/clustered deployments. |
| `FLASK_ENV` | Optional | `development` | Set to `production` in live deployments to activate strict security checks and secure cookie flags. |

### Generating Secrets

```bash
# Generate a cryptographic SECRET_KEY
python -c "import secrets; print(secrets.token_hex(32))"

# Copy the environment template
copy .env.example .env
```

## Getting Started

### 1. Frontend

```bash
# Frontend is served through Flask templates
```

### 2. Backend

```powershell
# Create and activate virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Create environment file
copy .env.example .env

# Start the backend server
python -m backend.main
```

## Post-Deployment Smoke Test Checklist

After deploying to Vercel (or updating environment variables), verify system health and resilience using the following automated curl checklist:

```bash
# Set your deployment target base URL (local or production)
BASE_URL="https://raahi-wine.vercel.app"

# 1. Platform Landing Page
curl -I -s "$BASE_URL/" | head -n 1
# Expected: HTTP/2 200 (or HTTP/1.1 200 OK)

# 2. Authentication View
curl -I -s "$BASE_URL/auth" | head -n 1
# Expected: HTTP/2 200

# 3. Live Health & Database Connection Ping
curl -s "$BASE_URL/health"
# Expected: {"database_connected":true,"status":"healthy"} (HTTP 200)

# 4. Air Quality Snapshot (Resilient WAQI Primary + Stale Cache Fallback)
curl -s "$BASE_URL/api/current-aqi"
# Expected: {"aqi":...,"city":"Mumbai","quality":...,"stale":...} (HTTP 200)

# 5. Western Line Transit Stations
curl -s "$BASE_URL/api/stations"
# Expected: Array of 27 Mumbai Western Line stations (HTTP 200)

# 6. Embedded Mumbai BEST Bus Depots (Zero Pandas Dependency)
curl -s "$BASE_URL/api/bus-depots"
# Expected: {"depots":[...],"success":true} (HTTP 200 with 20 verified depots)

# 7. User Registration & Session Cookie Validation
curl -i -s -c cookies.txt -X POST "$BASE_URL/auth/register" \
  -d "name=Commuter Test" \
  -d "email_or_phone=smoke_test_user@raahi.local" \
  -d "password=SecurePassword123!" | head -n 10
# Expected: HTTP 302 redirecting to /location-permission with session cookie set

# 8. User Login with Session
curl -i -s -c cookies.txt -X POST "$BASE_URL/auth/login" \
  -d "email_or_phone=smoke_test_user@raahi.local" \
  -d "password=SecurePassword123!" | head -n 10
# Expected: HTTP 302 redirecting to /home

# 9. Save Trip Input Validation (Negative Test - Expects 400 Bad Request)
curl -s -b cookies.txt -X POST "$BASE_URL/api/save-trip" \
  -H "Content-Type: application/json" \
  -d '{"mode":"Bus","distance_km":-5}'
# Expected: {"message":"Invalid destination: non-empty string under 255 characters required","status":"error"} (HTTP 400)

# 10. Rate Limiter Validation (Rapid Requests Trigger 429)
for i in {1..7}; do
  curl -s -o /dev/null -w "%{http_code}\n" -X POST "$BASE_URL/auth/login" \
    -d "email_or_phone=bad@test.local" -d "password=wrong"
done
# Expected: First 5 return 302, 6th and 7th return 429 Too Many Requests
```

## License

MIT License - see LICENSE for details.
