# PROMPTING_INSTRUCTIONS.md

## 📘 LLM Application — Prompting Instructions (for Cursor / AI Coding Assistant)

## 🔧 Project Overview
This project builds a **local-only LLM chatbot application** using:

- **Backend:** FastAPI (Python)
- **Frontend:** Next.js (App Router)
- **LLM:** OpenAI API (GPT models)
- **RAG:** LangChain
- **Vector Database:** FAISS (local)
- **Storage:** Local **PostgreSQL** for chat history and user accounts
- **Authentication:** Local register/login/logout
- **Development Scope:** Local development only (no CI/CD or cloud deployment)

---

## 🎯 Primary Objectives
- Build a chatbot UI with **streaming responses**
- Integrate OpenAI GPT models for text generation
- Implement RAG using **LangChain + FAISS**
- Allow users to upload documents → chunk → embed → store
- Retrieve relevant chunks via FAISS at query time
- Support **user registration, login, logout**
- Persist chat history and user accounts in **PostgreSQL**
- Provide clean, modular, well-structured code

---

## 📂 Required Features

### 1. Chat Interface (Frontend)
- Streaming chat (SSE or fetch streaming)
- Markdown + code block rendering
- Chat history stored in PostgreSQL (per user)
- Modern UI using:
  - TailwindCSS
  - shadcn/ui
  - React Query or SWR
- Auth UI:
  - Registration form
  - Login form
  - Logout button

### 2. Backend (FastAPI)
- `/api/chat` endpoint:
  - Requires user authentication
  - Accepts user messages
  - Retrieves relevant documents (RAG)
  - Calls OpenAI LLM
  - Streams the response
  - Stores chat messages in PostgreSQL

- `/api/documents/upload` endpoint:
  - Requires login
  - Accepts file upload
  - Extracts text from PDF, TXT, MD, DOCX
  - Chunks using LangChain
  - Embeds using OpenAI Embeddings
  - Saves vectors into local FAISS index

- `/api/rag/query` endpoint:
  - Requires login
  - Returns retrieved documents only

- `/api/auth/register` endpoint:
  - Registers a new user
  - Stores user credentials in PostgreSQL (hashed passwords)

- `/api/auth/login` endpoint:
  - Validates credentials
  - Returns a session token (JWT or simple token)

- `/api/auth/logout` endpoint:
  - Invalidates session/token

### 3. RAG System (LangChain)
- Use `RecursiveCharacterTextSplitter` for chunking
- Use `OpenAIEmbeddings` for embedding
- Store vectors in a **local FAISS index**
- Save documents + metadata locally as JSON or in PostgreSQL if needed
- Provide retrieval (top-k) during queries

---

## 🧩 Tech Stack Rules

### Backend Rules (Python)
- Use **FastAPI** with async endpoints
- Use `langchain`, `langchain-openai`, `langchain-community`
- Use **faiss-cpu** for local vector storage
- Use **pydantic** for request/response models
- Use **python-multipart** for file uploads
- Use **passlib** for password hashing
- Use `asyncpg` or SQLAlchemy for PostgreSQL integration
- Optionally, use JWT (`pyjwt`) for session management
- All endpoints that access chat or documents must **require authentication**

### Frontend Rules (Next.js)
- Use **App Router**
- Use **TailwindCSS** + **shadcn/ui**
- Use **SWR** or **React Query**
- Use `EventSource` or fetch streaming for `/chat`
- Use `react-markdown` + `highlight.js`
- Provide auth pages/components for register/login/logout

### LLM Rules
- Always call OpenAI via user’s API key
- Recommended models:
  - `gpt-4o-mini` (default)
  - `gpt-4.1` (complex tasks)
  - `o1-mini` / `o1-preview` (reasoning)
- Use `text-embedding-3-small` for embeddings

---

## 🚫 Do NOT Include
Do NOT generate code for:

- CI/CD (GitHub Actions, GitLab CI, etc.)
- Cloud deployment (AWS, GCP, Azure)
- Docker, Kubernetes, Terraform, Pulumi
- Production logging/monitoring/tracing
- OAuth or external authentication
- Billing/subscriptions

Keep everything **local** and simple.

---

## 🧠 Coding Style Guide

### Backend
- Async FastAPI endpoints
- Type hints everywhere
- Clear module naming (`ingest.py`, `retriever.py`, `auth.py`)
- Small, clean functions
- Use structured JSON or streaming responses
- Hash passwords before storing
- Validate session/auth tokens for protected endpoints
- Store chat messages and user accounts in **PostgreSQL**

### Frontend
- Prefer server components unless client features needed
- Use React Hooks
- Extract UI into reusable components
- Use async/await with fetch
- Avoid unnecessary re-renders
- Provide auth forms for register/login/logout

---

## 🤖 AI Assistant Behavior Guidelines

When generating code:
- Follow this architecture strictly.
- Keep code modular, readable, and well-typed.
- Add comments for non-trivial logic.
- Provide file paths and filenames for multi-file outputs.
- **If the AI does not know or is unclear about what to do next, it must ask the user for clarification instead of hallucinating or making things up.**
- Validate database interactions and authentication logic.
- Ensure frontend and backend follow the PostgreSQL + FAISS + OpenAI setup.
