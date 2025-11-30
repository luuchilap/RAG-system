/**
 * API client functions for communicating with the backend.
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

interface RegisterRequest {
  username: string
  email: string
  password: string
}

interface LoginRequest {
  username: string
  password: string
}

interface AuthResponse {
  access_token: string
  token_type: string
  user?: {
    id: string
    username: string
    email: string
    created_at: string
  }
}

interface User {
  id: string
  username: string
  email: string
  created_at: string
}

/**
 * Get the stored authentication token from localStorage.
 */
function getToken(): string | null {
  if (typeof window === "undefined") return null
  return localStorage.getItem("auth_token")
}

/**
 * Set the authentication token in localStorage.
 */
function setToken(token: string): void {
  if (typeof window === "undefined") return
  localStorage.setItem("auth_token", token)
}

/**
 * Remove the authentication token from localStorage.
 */
function removeToken(): void {
  if (typeof window === "undefined") return
  localStorage.removeItem("auth_token")
}

/**
 * Make an authenticated API request.
 */
async function authenticatedFetch(
  endpoint: string,
  options: RequestInit = {}
): Promise<Response> {
  const token = getToken()
  const headers = new Headers(options.headers)

  if (token) {
    headers.set("Authorization", `Bearer ${token}`)
  }

  return fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  })
}

/**
 * Register a new user.
 */
export async function register(
  data: RegisterRequest
): Promise<AuthResponse> {
  const response = await fetch(`${API_BASE_URL}/api/auth/register`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || "Registration failed")
  }

  const result: AuthResponse = await response.json()
  if (result.access_token) {
    setToken(result.access_token)
  }
  return result
}

/**
 * Login a user.
 */
export async function login(data: LoginRequest): Promise<AuthResponse> {
  const formData = new FormData()
  formData.append("username", data.username)
  formData.append("password", data.password)

  const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
    method: "POST",
    body: formData,
  })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || "Login failed")
  }

  const result: AuthResponse = await response.json()
  if (result.access_token) {
    setToken(result.access_token)
  }
  return result
}

/**
 * Logout the current user.
 */
export async function logout(): Promise<void> {
  try {
    await authenticatedFetch("/api/auth/logout", {
      method: "POST",
    })
  } finally {
    removeToken()
  }
}

/**
 * Get the current authenticated user.
 */
export async function getCurrentUser(): Promise<User> {
  const response = await authenticatedFetch("/api/auth/me")

  if (!response.ok) {
    if (response.status === 401) {
      removeToken()
      throw new Error("Unauthorized")
    }
    const error = await response.json()
    throw new Error(error.detail || "Failed to get user")
  }

  return response.json()
}

/**
 * Check if user is authenticated.
 */
export function isAuthenticated(): boolean {
  return getToken() !== null
}

// Chat API types and functions

export interface ChatMessage {
  id: string
  role: "user" | "assistant"
  content: string
  timestamp: string
  conversation_id?: string
}

export interface ChatRequest {
  message: string
  conversation_id?: string
}

export interface Conversation {
  conversation_id: string
  last_timestamp?: string
  message_count: number
  last_message?: string
}

export interface ChatHistoryResponse {
  conversation_id?: string
  messages?: ChatMessage[]
  conversations?: Conversation[]
}

/**
 * Send a chat message and stream the response.
 * Returns a ReadableStream for SSE processing.
 */
export async function sendChatMessage(
  message: string,
  conversationId?: string
): Promise<{ response: Response; conversationId: string | null }> {
  const token = getToken()
  if (!token) {
    throw new Error("Not authenticated")
  }

  const response = await fetch(`${API_BASE_URL}/api/chat/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({
      message,
      conversation_id: conversationId || null,
    }),
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Chat request failed" }))
    throw new Error(error.detail || "Chat request failed")
  }

  const responseConversationId = response.headers.get("X-Conversation-Id")

  return { response, conversationId: responseConversationId }
}

/**
 * Get chat history for a conversation or list all conversations.
 */
export async function getChatHistory(
  conversationId?: string
): Promise<ChatHistoryResponse> {
  const url = conversationId
    ? `${API_BASE_URL}/api/chat/history?conversation_id=${conversationId}`
    : `${API_BASE_URL}/api/chat/history`

  const response = await authenticatedFetch(url)

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || "Failed to get chat history")
  }

  return response.json()
}

/**
 * Delete a conversation.
 */
export async function deleteConversation(conversationId: string): Promise<void> {
  const response = await authenticatedFetch(`/api/chat/conversation/${conversationId}`, {
    method: "DELETE",
  })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || "Failed to delete conversation")
  }
}

// Document API types and functions

export interface Document {
  id: string
  filename: string
  file_type: string
  file_size: number | null
  chunk_count: number | null
  uploaded_at: string
}

export interface DocumentUploadResponse {
  document_id: string
  filename: string
  chunk_count: number
  status: string
}

export interface DocumentsResponse {
  documents: Document[]
}

/**
 * Upload a document file.
 */
export async function uploadDocument(
  file: File,
  onProgress?: (progress: number) => void
): Promise<DocumentUploadResponse> {
  const token = getToken()
  if (!token) {
    throw new Error("Not authenticated")
  }

  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest()
    const formData = new FormData()
    formData.append("file", file)

    // Track upload progress
    xhr.upload.addEventListener("progress", (event) => {
      if (event.lengthComputable && onProgress) {
        const percentComplete = Math.round((event.loaded / event.total) * 100)
        onProgress(percentComplete)
      }
    })

    xhr.onload = function () {
      if (xhr.status === 200) {
        try {
          const response: DocumentUploadResponse = JSON.parse(xhr.responseText)
          resolve(response)
        } catch (error) {
          reject(new Error("Failed to parse response"))
        }
      } else {
        try {
          const error = JSON.parse(xhr.responseText)
          reject(new Error(error.detail || "Upload failed"))
        } catch {
          reject(new Error(`Upload failed: ${xhr.statusText}`))
        }
      }
    }

    xhr.onerror = function () {
      reject(new Error("Upload failed. Please try again."))
    }

    xhr.open("POST", `${API_BASE_URL}/api/documents/upload`)
    xhr.setRequestHeader("Authorization", `Bearer ${token}`)
    xhr.send(formData)
  })
}

/**
 * Get all documents for the current user.
 */
export async function getDocuments(): Promise<DocumentsResponse> {
  const response = await authenticatedFetch("/api/documents/")

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || "Failed to get documents")
  }

  return response.json()
}

/**
 * Delete a document.
 */
export async function deleteDocument(documentId: string): Promise<void> {
  const response = await authenticatedFetch(`/api/documents/${documentId}`, {
    method: "DELETE",
  })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || "Failed to delete document")
  }
}

