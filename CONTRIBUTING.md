# Contributing to Raahi

Thank you for your interest in contributing to Raahi! This document provides guidelines for contributing to the project.

## Project Structure

```
raahi/
├── backend/              # Flask backend application
│   ├── routes/          # Route handlers (auth, api, web, admin, ml)
│   ├── services/        # Business logic (11 services)
│   ├── database/        # SQLAlchemy models & extensions
│   ├── pdf_export_service/  # Node.js microservice for PDF generation
│   └── utils/          # Helper functions
├── raahi_ml/           # Machine learning pipeline
│   ├── data/           # Raw and processed datasets
│   ├── models/         # Trained ML models
│   ├── pipelines/      # Training and preprocessing
│   └── config/         # ML configuration
├── frontend/           # Frontend templates & static assets
│   ├── templates/      # HTML pages
│   └── static/        # CSS, JavaScript, images
├── config/            # Application configuration
├── scripts/           # Utility scripts
├── logs/              # Application logs
├── docs/              # Documentation & exports
├── tests/             # Test suite
└── instance/          # Instance-specific files (databases, etc.)
```

## Development Setup

### Prerequisites
- Python 3.13+
- Node.js 20+
- PostgreSQL 15+
- Git

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yashvieeeeee/Raahi.git
   cd Raahi
   ```

2. **Set up Python environment:**
   ```bash
   python -m venv .venv
   .venv\Scripts\Activate  # Windows
   source .venv/bin/activate  # Linux/Mac
   pip install -r requirements.txt
   ```

3. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your PostgreSQL credentials and API keys
   ```

4. **Set up Node.js dependencies (for PDF service):**
   ```bash
   cd backend/pdf_export_service
   npm install
   cd ../..
   ```

5. **Initialize database:**
   ```bash
   python -m backend.main
   # This will create tables automatically
   ```

## Running the Project

### Backend
```bash
python -m backend.main
# Runs on http://localhost:5000
```

### PDF Export Service (separate terminal)
```bash
cd backend/pdf_export_service
npm start
# Runs on http://localhost:3000
```

### Docker Compose
```bash
docker-compose up -d
```

## Code Style & Standards

### Python
- Follow PEP 8
- Use snake_case for variables and functions
- Use type hints where applicable
- Keep functions focused and under 50 lines

### JavaScript/Node.js
- Use ES6+ syntax
- Use camelCase for variables and functions
- Add JSDoc comments for functions

### File Organization
- One class per file in models
- Related functions together in services
- Alphabetical imports

## Testing

Run tests before submitting PRs:
```bash
pytest tests/ -v
```

## Commit Messages

Use descriptive commit messages:
```
feat: add new feature description
fix: fix bug description
refactor: improve code structure
docs: update documentation
test: add/update tests
chore: maintenance tasks
```

## Pull Request Process

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make your changes
3. Run tests: `pytest tests/ -v`
4. Commit with descriptive messages
5. Push to your fork
6. Create a Pull Request with:
   - Clear description of changes
   - Reference to related issues
   - Screenshots (if UI changes)

## Known Issues

- PDF export requires Puppeteer (headless Chrome) - large binary
- ML model predictions require loaded .pkl files
- PostgreSQL required (SQLite fallback available for development)

## Performance Guidelines

- Keep API responses under 500ms
- Cache expensive queries
- Lazy load ML models on first request
- Use connection pooling for database

## Security Guidelines

- Never commit .env files (use .env.example)
- Validate all user inputs
- Use parameterized queries (SQLAlchemy ORM)
- Keep dependencies updated

## Questions?

- Check [ARCHITECTURE.md](docs/ARCHITECTURE.md) for project overview
- Review service documentation in [backend/](backend/)
- Open an issue for questions

---

Happy contributing! 🚀
