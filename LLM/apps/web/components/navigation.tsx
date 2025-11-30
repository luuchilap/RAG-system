"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { Button } from "@workspace/ui/components/button"
import { useAuth } from "@/hooks/useAuth"

export function Navigation() {
  const pathname = usePathname()
  const { user, logout, loading } = useAuth()

  const isActive = (path: string) => pathname === path

  return (
    <nav className="border-b bg-background">
      <div className="container mx-auto px-4">
        <div className="flex h-16 items-center justify-between">
          <div className="flex items-center gap-6">
            <Link href="/" className="text-xl font-bold">
              LLM Chatbot
            </Link>
            {!loading && user && (
              <div className="hidden md:flex gap-4">
                <Link
                  href="/chat"
                  className={`text-sm font-medium transition-colors hover:text-primary ${
                    isActive("/chat") ? "text-primary" : "text-muted-foreground"
                  }`}
                >
                  Chat
                </Link>
                <Link
                  href="/documents"
                  className={`text-sm font-medium transition-colors hover:text-primary ${
                    isActive("/documents")
                      ? "text-primary"
                      : "text-muted-foreground"
                  }`}
                >
                  Documents
                </Link>
              </div>
            )}
          </div>
          <div className="flex items-center gap-4">
            {loading ? (
              <div className="text-sm text-muted-foreground">Loading...</div>
            ) : user ? (
              <>
                <span className="text-sm text-muted-foreground">
                  {user.username}
                </span>
                <Button variant="outline" size="sm" onClick={logout}>
                  Logout
                </Button>
              </>
            ) : (
              <>
                <Link href="/login">
                  <Button variant="ghost" size="sm">
                    Login
                  </Button>
                </Link>
                <Link href="/register">
                  <Button size="sm">Register</Button>
                </Link>
              </>
            )}
          </div>
        </div>
      </div>
    </nav>
  )
}

