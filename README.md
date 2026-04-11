# Raahi

Raahi is a Flask-based commuting assistant with a separated backend, frontend, and machine learning workspace.

## Structure

- `backend/`: Flask app factory, routes, services, and database modules.
- `frontend/`: Templates and static assets.
- `raahi_ml/`: Datasets, notebooks, trained models, and ML pipelines.
- `instance/`: SQLite database files.
- `config/`: Application configuration.
- `scripts/`: One-off operational and migration utilities.

## Run

```bash
python -m backend.main
```

## Notes

- SQLite defaults to `instance/raahi.db`.
- PostgreSQL can be enabled with `DATABASE_URL` or the provided Docker Compose file.
- Model assets and datasets now load from `raahi_ml/`.
