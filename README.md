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

### 1. Vercel-Ready Deployment

Raahi is configured for Vercel using `pyproject.toml` with the Flask entrypoint:

```toml
[tool.vercel]
entrypoint = "backend.main:app"
```

### 2. Lightweight Production Build

Vercel serverless functions have strict bundle limits, so the production deployment keeps dependencies lightweight. Heavy ML packages are optional and better suited for local development or a separate ML service.

### 3. Safer Startup

The app logs database initialization errors instead of crashing immediately. Public pages can still load, while login and database-backed pages require a valid `DATABASE_URL`.

### 4. Cleaner Deployment Package

`.vercelignore` excludes local-only files like `.venv`, logs, notebooks, datasets, and generated model artifacts.

## Technical Features

### Backend

Built with Flask, Flask-Login, and Flask-SQLAlchemy. Routes are split by purpose: auth, web pages, APIs, admin tools, and optional ML endpoints.

### Database

Uses PostgreSQL through SQLAlchemy. Local development can use Docker PostgreSQL, while production should use an externally reachable cloud database URL.

### Route and AQI Intelligence

Raahi combines route distance estimates, fare calculations, emissions estimates, and AQI data to help users compare travel choices.

### Optional ML Layer

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

### 1. Clone the Project

```bash
git clone https://github.com/yashvieeeeee/Raahi.git
cd Raahi
```

### 2. Create a Virtual Environment

```powershell
python -m venv .venv
.venv\Scripts\Activate
```

