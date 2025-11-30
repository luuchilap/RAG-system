"use client"

import { useState, useEffect, useRef } from "react"
import { useRouter, useSearchParams } from "next/navigation"
import { MessageList, Message } from "./MessageList"
import { MessageInput } from "./MessageInput"
import { sendChatMessage, getChatHistory, getDocuments } from "@/lib/api"
import { useAuth } from "@/hooks/useAuth"
import { Alert, AlertDescription } from "@workspace/ui/components/alert"
import { FileText } from "lucide-react"

export function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [conversationId, setConversationId] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [hasDocuments, setHasDocuments] = useState<boolean | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const router = useRouter()
  const searchParams = useSearchParams()
  const { user } = useAuth()

  // Check if user has documents
  const checkUserDocuments = async () => {
    try {
      const data = await getDocuments()
      setHasDocuments(data.documents.length > 0)
    } catch (error) {
      console.error("Error checking documents:", error)
      setHasDocuments(false)
    }
  }

  // Load conversation from URL or initialize
  useEffect(() => {
    const urlConversationId = searchParams.get("conversation")
    if (urlConversationId) {
      setConversationId(urlConversationId)
      loadConversationHistory(urlConversationId)
    }
  }, [searchParams])

  // Check for documents on mount
  useEffect(() => {
    if (user) {
      checkUserDocuments()
    }
  }, [user])

  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  const loadConversationHistory = async (convId: string) => {
    try {
      const history = await getChatHistory(convId)
      if (history.messages) {
        setMessages(
          history.messages.map((msg) => ({
            id: msg.id,
            role: msg.role,
            content: msg.content,
            timestamp: msg.timestamp,
          }))
        )
      }
    } catch (err) {
      console.error("Failed to load conversation history:", err)
      setError("Failed to load conversation history")
    }
  }

  const handleSendMessage = async (content: string) => {
    if (!content.trim() || isLoading) return

    setError(null)

    // Add user message to state immediately
    const userMessage: Message = {
      id: `user-${Date.now()}`,
      role: "user",
      content,
      timestamp: new Date().toISOString(),
    }

    setMessages((prev) => [...prev, userMessage])

    // Add empty assistant message for streaming
    const assistantMessageId = `assistant-${Date.now()}`
    const assistantMessage: Message = {
      id: assistantMessageId,
      role: "assistant",
      content: "",
      timestamp: new Date().toISOString(),
      isStreaming: true,
    }

    setMessages((prev) => [...prev, assistantMessage])
    setIsLoading(true)

    try {
      const { response, conversationId: newConversationId } = await sendChatMessage(
        content,
        conversationId || undefined
      )

      // Update conversation ID if this is a new conversation
      if (newConversationId && !conversationId) {
        setConversationId(newConversationId)
        router.push(`/chat?conversation=${newConversationId}`)
      }

      // Process streaming response (SSE format)
      const reader = response.body?.getReader()
      if (!reader) {
        throw new Error("No response body")
      }

      const decoder = new TextDecoder()
      let assistantContent = ""
      let buffer = ""

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        // SSE events are separated by \n\n
        const events = buffer.split("\n\n")
        // Keep the last incomplete event in buffer
        buffer = events.pop() || ""

        for (const event of events) {
          const lines = event.split("\n")
          for (const line of lines) {
            if (line.startsWith("data: ")) {
              const content = line.slice(6) // Remove "data: " prefix, preserve all content including spaces
              if (content && !content.startsWith("[ERROR]")) {
                assistantContent += content
                // Update assistant message with streaming content
                setMessages((prev) =>
                  prev.map((msg) =>
                    msg.id === assistantMessageId
                      ? { ...msg, content: assistantContent, isStreaming: true }
                      : msg
                  )
                )
              } else if (content?.startsWith("[ERROR]")) {
                throw new Error(content.slice(7).trim())
              }
            }
          }
        }
      }

      // Process any remaining buffer
      if (buffer) {
        const lines = buffer.split("\n")
        for (const line of lines) {
          if (line.startsWith("data: ")) {
            const content = line.slice(6)
            if (content && !content.startsWith("[ERROR]")) {
              assistantContent += content
              setMessages((prev) =>
                prev.map((msg) =>
                  msg.id === assistantMessageId
                    ? { ...msg, content: assistantContent, isStreaming: true }
                    : msg
                )
              )
            }
          }
        }
      }

      // Mark streaming as complete
      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === assistantMessageId
            ? { ...msg, isStreaming: false }
            : msg
        )
      )
    } catch (err) {
      console.error("Error sending message:", err)
      setError(err instanceof Error ? err.message : "Failed to send message")
      // Remove the assistant message on error
      setMessages((prev) => prev.filter((msg) => msg.id !== assistantMessageId))
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="flex flex-col h-[calc(100vh-4rem)]">
      {error && (
        <div className="bg-destructive/10 text-destructive px-4 py-2 text-sm text-center">
          {error}
        </div>
      )}
      {hasDocuments === false && (
        <Alert className="m-4 mb-0 border-amber-200 bg-amber-50">
          <FileText className="h-4 w-4" />
          <AlertDescription className="text-amber-800">
            <span className="font-medium">No documents uploaded.</span>{" "}
            <a href="/documents" className="underline hover:text-amber-900">
              Upload documents
            </a>{" "}
            to enable document-aware responses.
          </AlertDescription>
        </Alert>
      )}
      {hasDocuments === true && (
        <Alert className="m-4 mb-0 border-blue-200 bg-blue-50">
          <FileText className="h-4 w-4 text-blue-600" />
          <AlertDescription className="text-blue-800">
            <span className="font-medium">Document-aware mode active.</span> Your responses will use context from your uploaded documents when relevant.
          </AlertDescription>
        </Alert>
      )}
      <MessageList messages={messages} />
      <div ref={messagesEndRef} />
      <MessageInput onSendMessage={handleSendMessage} isLoading={isLoading} />
    </div>
  )
}

