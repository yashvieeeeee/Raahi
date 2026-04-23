# PostgreSQL Migration Guide for Raahi

## Why PostgreSQL?

PostgreSQL is a solid production database with:
- good concurrency support
- reliable backups and restore tooling
- flexible data types
- mature user and permission management

## Setup Options

### Option 1: Docker

1. Install Docker.
2. Copy `.env.example` to `.env`.
3. Replace the placeholder database values in `.env`.
4. Start PostgreSQL:

```bash
docker-compose up -d
```

5. Verify the container:

```bash
docker-compose logs postgres
```

### Option 2: Local PostgreSQL Installation

1. Install PostgreSQL.
2. Set the database values in `.env`.
3. Run the setup script:

```bash
python scripts/setup_postgres.py
```

## Required Environment Variables

```bash
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=your_database_name
POSTGRES_USER=your_database_user
POSTGRES_PASSWORD=change-this-database-password
POSTGRES_ADMIN_USER=postgres
POSTGRES_ADMIN_PASSWORD=change-this-admin-password

DATABASE_URL=postgresql://your_database_user:change-this-database-password@localhost:5432/your_database_name
SECRET_KEY=your-secret-key-here-change-in-production
```

## Migration Steps

1. Install Python dependencies:

```bash
pip install -r requirements.txt
```

2. Start PostgreSQL.
3. Run the migration:

```bash
python scripts/migrate_to_postgres.py
```

4. Start the app and verify it connects.

## Troubleshooting

Check container status:

```bash
docker-compose ps postgres
```

Check logs:

```bash
docker-compose logs postgres
```

Test the configured connection:

```bash
python -c "import os, psycopg2; conn = psycopg2.connect(os.environ['DATABASE_URL']); print('Connected')"
```

## Rollback

To switch back to SQLite:

```bash
DATABASE_URL=sqlite:///raahi.db
```

## References

- PostgreSQL docs: https://www.postgresql.org/docs/
- psycopg docs: https://www.psycopg.org/docs/
- Docker Postgres image: https://hub.docker.com/_/postgres
