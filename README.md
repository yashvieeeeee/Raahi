# 🚌 Raahi - Smart Commuting Assistant

Raahi is an intelligent commuting assistant that helps users optimize their public transportation journey with real-time air quality data, fare predictions, and route recommendations. Built with Flask, PostgreSQL, and machine learning models.

Live app: `https://raahi-wine.vercel.app`

## Features

- Plan routes across train, bus, auto, and walking options
- Show travel time, cost, CO2, and AQI-aware suggestions
- Let users register, log in, and save trips
- Provide profile and admin dashboards
- Support optional ML advisory features for local/full deployments

## Tech Stack

| Backend - Flask, Flask-Login, Flask-SQLAlchemy 
| Frontend - Jinja2, CSS, JavaScript 
| Database - PostgreSQL 
| APIs -  Google Maps, WAQI, OpenAQ
| Deployment - Vercel 
| Optional ML - pandas, scikit-learn, XGBoost, joblib

## Project Map

```text
backend/      Flask routes, services, database models
frontend/     Templates, styles, scripts, images
raahi_ml/     Optional ML pipelines and model helpers
config/       App settings
scripts/      Utility and database scripts
tests/        Test files
```

## Run Locally

```bash
git clone https://github.com/yashvieeeeee/Raahi.git
cd Raahi
python -m venv .venv
```

Activate the environment:

```powershell
.venv\Scripts\Activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create your `.env` file:

```powershell
copy .env.example .env
```

Start the app:

```bash
python -m backend.main
```

Open:

```text
http://localhost:5000
```

## Environment Variables

Set these in `.env` locally and in Vercel for production:

```env
DATABASE_URL=postgresql://USER:PASSWORD@HOST:5432/DATABASE
SECRET_KEY=your-secret-key
GOOGLE_MAPS_API_KEY=optional
WAQI_API_TOKEN=optional
OPENAQ_API_KEY=optional
```

For Render PostgreSQL, use the **External Database URL** in Vercel.

## Test

```bash
python -m pytest tests -q
```

## License
No license has been specified yet.
