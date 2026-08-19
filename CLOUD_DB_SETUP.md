# 🚀 Cloud Database Setup Guide - Render PostgreSQL

## Step 1: Create Render PostgreSQL Database (Free Tier)

1. Go to [render.com](https://render.com)
2. Sign up for a free account
3. Click **"New +"** → Select **"PostgreSQL"**
4. Configure:
   - **Name**: `raahi-postgres`
   - **Database**: `raahi`
   - **User**: `raahi_user`
   - **Region**: Choose closest to your location
   - **Plan**: Free tier (no credit card required initially)
5. Click **"Create Database"**
6. Wait 5-10 minutes for database to spin up
7. **Copy the connection string** (looks like: `postgresql://raahi_user:xxxxx@xxx.render.com:5432/raahi`)

## Step 2: Add Connection String to Vercel

1. Go to your Vercel project: [vercel.com/dashboard](https://vercel.com/dashboard)
2. Select your Raahi project
3. Go to **Settings** → **Environment Variables**
4. Add new variable:
   - **Name**: `DATABASE_URL`
   - **Value**: Paste the Render connection string
   - **Select**: Production
5. Click **Add** and redeploy

## Step 3: Local Development Setup

For local development, use Docker PostgreSQL (already in docker-compose.yml):

```bash
# Start local PostgreSQL
docker-compose up -d

# Verify it's running
docker ps
```

Your `.env` file should have:
```env
# Local development
DATABASE_URL=postgresql://raahi_user:raahi_password@localhost:5432/raahi

# Or use production (Render):
# DATABASE_URL=postgresql://raahi_user:xxxxx@xxx.render.com:5432/raahi
```

## Step 4: Verify Connection

```bash
# Test the connection from Flask
cd C:\Raahi
python -m pip install -q psycopg2-binary
python -c "from backend.main import app; print('✓ Database connection OK')"
```

## ⚠️ Important Notes

- **Free tier limitations**: Render free PostgreSQL databases are deleted after 90 days of inactivity
- **Backups**: Keep important data backed up
- **Cost**: Upgrade to paid plan when moving to production ($7-50+/month)

## 🔗 Connection Details Summary

| Environment | Host | Port | Database | User |
|---|---|---|---|---|
| Local | localhost | 5432 | raahi | raahi_user |
| Vercel (Render) | xxx.render.com | 5432 | raahi | raahi_user |

