# PostgreSQL Migration Guide for Raahi

## 🐘 Why PostgreSQL?

PostgreSQL is a powerful, open-source database that offers:
- ✅ **Free and open-source** - No licensing costs
- ✅ **Better performance** - Handles concurrent users efficiently
- ✅ **Advanced features** - JSON, arrays, full-text search
- ✅ **Production-ready** - Scalable and reliable
- ✅ **Better security** - Robust user management

## 📋 Setup Options

### Option 1: Docker (Recommended - Easiest)

1. **Install Docker** on your system
2. **Run PostgreSQL:**
   ```bash
   docker-compose up -d
   ```
3. **Verify installation:**
   ```bash
   docker-compose logs postgres
   ```

### Option 2: Local PostgreSQL Installation

1. **Install PostgreSQL:**
   - **Windows:** Download from postgresql.org
   - **Mac:** `brew install postgresql`
   - **Linux:** `sudo apt-get install postgresql postgresql-contrib`

2. **Setup database:**
   ```bash
   python setup_postgres.py
   ```

## 🔄 Migration Steps

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start PostgreSQL:**
   - **Docker:** `docker-compose up -d`
   - **Local:** PostgreSQL service should be running

3. **Run migration:**
   ```bash
   python migrate_to_postgres.py
   ```

4. **Test the application:**
   ```bash
   python app_raahi.py
   ```

## 🔧 Configuration

### Environment Variables (.env file)

```bash
# PostgreSQL Configuration
POSTGRES_HOST=localhost
POSTGRES_DB=raahi_db
POSTGRES_USER=raahi_user
POSTGRES_PASSWORD=raahi_password
POSTGRES_PORT=5432

# Flask Configuration
SECRET_KEY=raahi-secret-key-fallback-2024
DATABASE_URL=postgresql://raahi_user:raahi_password@localhost:5432/raahi_db
```

## 📊 Database Schema

### Users Table
- `id` - Primary key
- `name` - User's full name
- `email` - Email address (unique)
- `password_hash` - Encrypted password
- `location` - User's saved location
- `co2_saved` - Total CO2 emissions saved
- `money_saved` - Total money saved
- `trips_taken` - Number of trips completed

### Trips Table
- `id` - Primary key
- `user_id` - Foreign key to Users table
- `destination` - Trip destination
- `mode` - Transportation mode
- `distance_km` - Trip distance
- `co2_emitted` - CO2 emissions
- `cost` - Trip cost
- `timestamp` - When trip was taken

## 🚀 Benefits After Migration

### Performance
- **Faster queries** with proper indexing
- **Better concurrency** for multiple users
- **Connection pooling** support

### Features
- **JSON support** for future features
- **Full-text search** capabilities
- **Advanced analytics** functions

### Production Ready
- **Backup tools** (pg_dump, pg_restore)
- **Replication** support
- **Monitoring** capabilities

## 🛠️ Troubleshooting

### Connection Issues
```bash
# Check PostgreSQL status
docker-compose ps postgres

# View logs
docker-compose logs postgres

# Test connection
python -c "import psycopg2; conn = psycopg2.connect('postgresql://raahi_user:raahi_password@localhost:5432/raahi_db'); print('✅ Connected!')"
```

### Migration Issues
```bash
# Backup SQLite data first
cp raahi.db raahi_backup.db

# Check SQLite data
sqlite3 raahi.db ".tables"

# Re-run migration
python migrate_to_postgres.py
```

## 🔄 Rolling Back

If you need to switch back to SQLite:

1. **Update .env file:**
   ```bash
   DATABASE_URL=sqlite:///raahi.db
   ```

2. **Use backup data:**
   ```bash
   cp raahi_backup.db raahi.db
   ```

## 📞 Support

- **PostgreSQL Documentation:** https://www.postgresql.org/docs/
- **psycopg2 Documentation:** https://www.psycopg.org/docs/
- **Docker PostgreSQL:** https://hub.docker.com/_/postgres
