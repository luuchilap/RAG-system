"use client"

import Link from "next/link"
import { Button } from "@workspace/ui/components/button"
import { useAuth } from "@/hooks/useAuth"
import { useEffect } from "react"
import { useRouter } from "next/navigation"

export default function HomePage() {
  const { isAuthenticated, loading } = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (!loading && isAuthenticated) {
      router.push("/chat")
    }
  }, [isAuthenticated, loading, router])

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[calc(100vh-4rem)]">
        <div className="text-muted-foreground">Loading...</div>
      </div>
    )
  }

  return (
    <div className="flex items-center justify-center min-h-[calc(100vh-4rem)]">
      <div className="flex flex-col items-center justify-center gap-6 text-center px-4">
        <h1 className="text-4xl font-bold">Local LLM Chatbot</h1>
        <p className="text-muted-foreground max-w-md">
          A local-only chatbot application with RAG capabilities. Upload
          documents and chat with AI using your own content.
        </p>
        <div className="flex gap-4">
          <Link href="/register">
            <Button size="lg">Get Started</Button>
          </Link>
          <Link href="/login">
            <Button variant="outline" size="lg">
              Login
            </Button>
          </Link>
        </div>
      </div>
    </div>
  )
}
