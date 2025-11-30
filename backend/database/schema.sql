-- PostgreSQL Database Schema for LLM Chatbot Application
-- This script creates the necessary tables for users, chat messages, and documents
-- It is idempotent and can be run multiple times safely

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create chat_messages table
CREATE TABLE IF NOT EXISTS chat_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    conversation_id UUID NOT NULL,
    role VARCHAR(50) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create documents table
CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_type VARCHAR(50) NOT NULL,
    file_size BIGINT,
    chunk_count INTEGER,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);

-- Create indexes for performance optimization
-- Index for chat messages by user and conversation
CREATE INDEX IF NOT EXISTS idx_chat_messages_user_conversation 
    ON chat_messages(user_id, conversation_id);

-- Index for chat messages by timestamp
CREATE INDEX IF NOT EXISTS idx_chat_messages_timestamp 
    ON chat_messages(timestamp);

-- Index for documents by user
CREATE INDEX IF NOT EXISTS idx_documents_user 
    ON documents(user_id);

-- Index for documents by uploaded_at for sorting
CREATE INDEX IF NOT EXISTS idx_documents_uploaded_at 
    ON documents(uploaded_at DESC);

-- Index for users by email for login lookups
CREATE INDEX IF NOT EXISTS idx_users_email 
    ON users(email);

-- Index for users by username for login lookups
CREATE INDEX IF NOT EXISTS idx_users_username 
    ON users(username);

