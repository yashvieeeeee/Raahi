# Contributing to Raahi

Thanks for helping improve Raahi. This guide covers the basics for setting up the project, making changes, and opening pull requests.

## Project Structure

```text
backend/                    Flask backend application
  main.py                   App factory and entrypoint
  routes/                   Auth, web, API, admin, and ML routes
  services/                 Business logic
  database/                 SQLAlchemy models and extensions
  utils/                    Shared helpers

frontend/                   Jinja templates and static assets
  templates/                HTML pages
  static/                   CSS, JavaScript, and images

raahi_ml/                   Optional ML pipelines and helpers
config/                     App configuration
scripts/                    Utility and database scripts
tests/                      Test files
```

## Development Setup and Installation

Clone the repository:

```bash
git clone https://github.com/yashvieeeeee/Raahi.git
cd Raahi
```

Create and activate a virtual environment:

```powershell
python -m venv .venv
.venv\Scripts\Activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a local environment file:

```powershell
copy .env.example .env
```

Run the app:

```bash
python -m backend.main
```

Open:

```text
http://localhost:5000
```

## Code Style and Standards

- Keep changes focused and easy to review.
- Follow the existing Flask route/service structure.
- Put business logic in `backend/services/`.
- Keep route handlers thin.
- Use clear names for functions, variables, and files.
- Do not commit `.env`, `.venv`, logs, database files, notebooks, or generated model files.
- Add comments only when they explain non-obvious logic.

## Pull Request Process

1. Create a branch:

```bash
git checkout -b feature/short-name
```

2. Make your changes.
3. Run the app locally.
4. Run tests if available:

```bash
python -m pytest tests -q
```

5. Commit with a clear message:

```text
fix: handle missing database connection
docs: clean up setup guide
feat: add route planner summary
```

6. Push your branch and open a pull request.

In your pull request, include:

- What changed
- Why the change was needed
- Screenshots for UI changes, if useful
- Any tests run or skipped

## Known Issues

- Full ML dependencies can be too large for Vercel serverless deployments.
- ML features may need local model files that are not committed to the repo.
- Database-backed pages require a valid `DATABASE_URL`.
- The PDF export service is separate from the main Flask app.

## Performance Guidelines

- Keep database queries simple and scoped.
- Avoid loading heavy ML assets during app startup.
- Keep Vercel production dependencies lightweight.
- Move expensive work into services instead of route handlers.
- Cache or reuse results when an API call or calculation is expensive.

## Questions?

- Check `README.md` for setup and deployment notes.
- Check `CLOUD_DB_SETUP.md` for cloud database setup.
- Open an issue if something is unclear or broken.
