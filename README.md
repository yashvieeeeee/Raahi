# 🚌 Raahi - Smart Commuting Assistant

Raahi is an intelligent commuting assistant that helps users optimize their public transportation journey with real-time air quality data, fare predictions, and route recommendations. Built with Flask, PostgreSQL, and machine learning models.

## ✨ Features

- 🗺️ **Smart Route Planning** - Get optimal routes using Google Maps API
- 🌍 **Air Quality Monitoring** - Real-time AQI and pollution levels from WAQI and OpenAQ
- 💰 **Fare Prediction** - ML-powered bus fare estimations
- 📊 **Analytics Dashboard** - Track trips and generate PDF reports
- 🚀 **Performance Optimized** - Sub-500ms API responses
- 🔐 **Secure** - PostgreSQL with SQLAlchemy ORM, session-based auth

## 📁 Project Structure

```
raahi/
├── backend/                      # Flask application
│   ├── main.py                  # App factory & entry point
│   ├── routes/                  # 5 route modules (auth, api, web, admin, ml)
│   ├── services/                # 11 business logic services
│   ├── database/                # SQLAlchemy models & extensions
│   ├── pdf_export_service/      # Node.js Puppeteer microservice
│   └── utils/                   # Helper functions
├── raahi_ml/                     # Machine learning pipeline
│   ├── data/                    # Raw & processed datasets
│   ├── models/                  # Trained .pkl models (16 total)
│   ├── pipelines/               # Training & preprocessing scripts
│   ├── notebooks/               # Jupyter notebooks
│   └── config/                  # ML hyperparameters
├── frontend/                     # Web UI
│   ├── templates/               # 8 HTML pages
│   └── static/                  # CSS, JavaScript, images
├── config/                       # Application settings
├── scripts/                      # Database & utility scripts
├── logs/                         # Application logs
├── docs/                         # Documentation & exports
├── tests/                        # Test suite
└── instance/                     # Instance-specific (databases, etc.)
```

## 🚀 Quick Start

### Prerequisites
- Python 3.13+
- Node.js 20+
- PostgreSQL 15+ (or SQLite for development)
- Git

### Installation

1. **Clone repository:**
   ```bash
   git clone https://github.com/yashvieeeeee/Raahi.git
   cd Raahi
   ```

2. **Setup Python environment:**
   ```bash
   python -m venv .venv
   .venv\Scripts\Activate  # Windows
   source .venv/bin/activate  # macOS/Linux
   pip install -r requirements.txt
   ```

3. **Configure environment:**
   ```bash
   copy .env.example .env  # Windows
   cp .env.example .env    # macOS/Linux
   ```
   Edit `.env` with your credentials (PostgreSQL, API keys)

4. **Setup Node.js for PDF service:**
   ```bash
   cd backend/pdf_export_service && npm install && cd ../..
   ```

5. **Run application:**
   ```bash
   python -m backend.main
   ```

Visit `http://localhost:5000`

## 🐳 Docker Setup

```bash
docker-compose up -d
```

## 📚 Architecture

### Backend Layer
- **Routes**: 5 modular route handlers (auth, web, api, admin, ml)
- **Services**: 11 business logic services (trip, route planner, ML advisory, air quality, etc.)
- **Database**: SQLAlchemy ORM with PostgreSQL (SQLite fallback)
- **PDF Export**: Node.js/Puppeteer microservice for report generation

### ML Layer
- Models: Fare prediction, emission estimation, delay forecasting, route optimization
- Framework: scikit-learn, XGBoost, pandas
- Data: 10 raw datasets + processed features
- Pipeline: Automated training and preprocessing

### Frontend Layer
- Templates: Bootstrap-based responsive design
- Features: Real-time map, trip history, analytics dashboard

## 🔌 API Integrations

- 🗺️ **Google Maps API** - Routes & geocoding
- 🌍 **WAQI** - World Air Quality Index
- 🚕 **OpenAQ** - Pollution measurements

## 📊 Technology Stack

| Component | Tech |
|-----------|------|
| Backend | Flask 3.0.3 |
| Database | PostgreSQL 15 / SQLite |
| ORM | SQLAlchemy 1.4.50 |
| ML | scikit-learn, XGBoost, pandas |
| PDF | Puppeteer (Node.js) |
| Auth | Flask-Login + sessions |
| Frontend | Jinja2, Bootstrap, folium |

## 🧪 Testing

```bash
pytest tests/ -v
```

## 📖 Documentation

- [CONTRIBUTING.md](CONTRIBUTING.md) - Contribution guidelines
- [docs/design.md](docs/design.md) - Architecture decisions
- [backend/](backend/) - Backend module overview

## 🔐 Security

- Environment variables in `.env` (not committed)
- SQLAlchemy ORM prevents SQL injection
- Session-based authentication
- Input validation on all endpoints

## 📈 Performance

- API responses: <500ms
- Model loading: ~1-2s
- Database pooling: Configured
- PDF generation: Async via Puppeteer

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on:
- Setting up development environment
- Code style standards
- Testing requirements
- Pull request process

## 📝 License

[Your License Here]

## 👤 Author

[Your Name]

---

**Ready to contribute?** Check out [CONTRIBUTING.md](CONTRIBUTING.md) and join the project!

**Questions?** Visit the [docs/](docs/) folder or open an issue.
