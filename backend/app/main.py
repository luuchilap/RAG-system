"""
Main FastAPI application entry point.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.config import settings
from app.database import init_db, close_db
from app.api import auth, chat, documents, rag


# Create FastAPI application with enhanced OpenAPI metadata
app = FastAPI(
    title="Local LLM Chatbot API",
    description="""
    Backend API for local LLM chatbot with RAG capabilities.
    
    ## Features
    
    * **Authentication**: User registration, login, and JWT token management
    * **Chat**: Streaming chat interface with OpenAI integration
    * **Documents**: Upload and process documents for RAG
    * **RAG**: Retrieve relevant document chunks based on queries
    
    ## Getting Started
    
    1. Register a new user at `/api/auth/register`
    2. Login to get an access token at `/api/auth/login`
    3. Use the token in the Authorization header: `Bearer <token>`
    4. Start chatting or uploading documents!
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    openapi_tags=[
        {
            "name": "auth",
            "description": "Authentication endpoints for user registration, login, and logout."
        },
        {
            "name": "chat",
            "description": "Chat endpoints for streaming conversations with AI."
        },
        {
            "name": "documents",
            "description": "Document management endpoints for uploading and managing documents."
        },
        {
            "name": "rag",
            "description": "RAG (Retrieval-Augmented Generation) endpoints for querying document embeddings."
        }
    ]
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(documents.router, prefix="/api/documents", tags=["documents"])
app.include_router(rag.router, prefix="/api/rag", tags=["rag"])


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize database connection on startup."""
    await init_db()


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Close database connection on shutdown."""
    await close_db()


# Health check endpoint
@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "message": "API is running"}


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Local LLM Chatbot API",
        "version": "1.0.0",
        "docs": "/docs"
    }


# Exception handlers
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    """Handle validation errors."""
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions."""
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )

