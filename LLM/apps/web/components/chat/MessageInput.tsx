"use client"

import { useState, KeyboardEvent } from "react"
import { Button } from "@workspace/ui/components/button"
import { Input } from "@workspace/ui/components/input"
import { Send } from "lucide-react"

interface MessageInputProps {
  onSendMessage: (content: string) => void
  isLoading?: boolean
}

export function MessageInput({ onSendMessage, isLoading = false }: MessageInputProps) {
  const [input, setInput] = useState("")

  const handleSend = () => {
    const trimmed = input.trim()
    if (trimmed && !isLoading) {
      onSendMessage(trimmed)
      setInput("")
    }
  }

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="border-t bg-background p-4">
      <div className="container mx-auto flex gap-2 max-w-4xl">
        <Input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Type your message..."
          disabled={isLoading}
          className="flex-1"
        />
        <Button onClick={handleSend} disabled={isLoading || !input.trim()} size="icon">
          <Send className="h-4 w-4" />
        </Button>
      </div>
    </div>
  )
}

