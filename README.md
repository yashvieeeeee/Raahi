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

## License

MIT License - see LICENSE for details.
