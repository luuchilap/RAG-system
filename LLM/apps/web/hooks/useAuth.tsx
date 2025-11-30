"use client"

import { createContext, useContext, useEffect, useState, ReactNode } from "react"
import { useRouter } from "next/navigation"
import * as api from "@/lib/api"

interface User {
  id: string
  username: string
  email: string
  created_at: string
}

interface AuthContextType {
  user: User | null
  loading: boolean
  login: (username: string, password: string) => Promise<void>
  register: (
    username: string,
    email: string,
    password: string
  ) => Promise<void>
  logout: () => Promise<void>
  isAuthenticated: boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)
  const router = useRouter()

  // Check if user is authenticated on mount
  useEffect(() => {
    const checkAuth = async () => {
      if (api.isAuthenticated()) {
        try {
          const userData = await api.getCurrentUser()
          setUser(userData)
        } catch (error) {
          // Token is invalid, clear it
          api.logout()
          setUser(null)
        }
      }
      setLoading(false)
    }

    checkAuth()
  }, [])

  const handleLogin = async (username: string, password: string) => {
    const response = await api.login({ username, password })
    if (response.user) {
      setUser(response.user)
      router.push("/chat")
    } else {
      // Fetch user data if not in response
      const userData = await api.getCurrentUser()
      setUser(userData)
      router.push("/chat")
    }
  }

  const handleRegister = async (
    username: string,
    email: string,
    password: string
  ) => {
    const response = await api.register({ username, email, password })
    if (response.user) {
      setUser(response.user)
      router.push("/chat")
    } else {
      // Fetch user data if not in response
      const userData = await api.getCurrentUser()
      setUser(userData)
      router.push("/chat")
    }
  }

  const handleLogout = async () => {
    await api.logout()
    setUser(null)
    router.push("/login")
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        login: handleLogin,
        register: handleRegister,
        logout: handleLogout,
        isAuthenticated: !!user,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider")
  }
  return context
}

