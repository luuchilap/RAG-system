# Backend Setup Guide

## Prerequisites

- Python 3.10+ (check with `python3 --version`)
- PostgreSQL installed and running
- Database `mydb` created

## Setup Steps

### 1. Create Virtual Environment

On macOS/Linux, use `python3` instead of `python`:

```bash
cd backend
python3 -m venv .venv
```

### 2. Activate Virtual Environment

**macOS/Linux:**
```bash
source .venv/bin/activate
```

**Windows:**
```bash
.venv\Scripts\activate
```

After activation, you should see `(.venv)` in your terminal prompt.

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

```bash
cp .env.example .env
# Edit .env with your configuration
```

The default `.env` should have:
```
DATABASE_URL=postgresql://postgres:lap@localhost:5432/mydb
SECRET_KEY=your-secret-key-change-in-production
```

### 5. Set Up Database

```bash
# Create database (if not exists)
createdb -U postgres mydb

# Run migrations
python -m app.database.migrations
```

### 6. Start the Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 7. Access Swagger UI

Open in browser: http://localhost:8000/docs

## Troubleshooting

### "python: command not found"
- Use `python3` instead of `python` on macOS/Linux
- After activating venv, `python` should work

### Database Connection Errors
- Ensure PostgreSQL is running: `pg_isready`
- Check database exists: `psql -U postgres -l | grep mydb`
- Verify connection string in `.env`

### Import Errors
- Make sure virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`

### Port Already in Use
- Change port: `uvicorn app.main:app --reload --port 8001`
- Or kill existing process on port 8000

