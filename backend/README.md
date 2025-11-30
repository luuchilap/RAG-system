# Backend API

FastAPI backend for the Local LLM Chatbot Application.

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Set up PostgreSQL database:**
   ```bash
   # Create the database
   createdb -U postgres mydb
   
   # Run migrations
   python -m app.database.migrations
   ```

4. **Run the development server:**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

## API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration settings
│   ├── database.py           # Database connection
│   ├── api/                  # API routes
│   │   ├── auth.py
│   │   ├── chat.py
│   │   ├── documents.py
│   │   └── rag.py
│   ├── models/               # Pydantic models
│   │   ├── user.py
│   │   ├── chat.py
│   │   └── document.py
│   ├── repositories/         # Database repositories
│   │   ├── user_repository.py
│   │   ├── chat_repository.py
│   │   └── document_repository.py
│   └── database/             # Database utilities
│       └── migrations.py
├── database/                 # SQL scripts
│   └── schema.sql
├── requirements.txt
└── README.md
```

