"use client"

import { useState, useCallback } from "react"
import {
  analyzeWeakness,
  getMockWeaknessAnalysis,
  WeaknessAnalysisResponse,
  TestType,
} from "@/lib/api"

interface UseWeaknessAnalysisReturn {
  analysis: WeaknessAnalysisResponse | null
  isLoading: boolean
  error: string | null
  fetchAnalysis: (testType?: TestType, limitAttempts?: number) => Promise<void>
  fetchMockAnalysis: () => Promise<void>
  clearAnalysis: () => void
}

/**
 * Hook for managing weakness analysis state and API calls.
 */
export function useWeaknessAnalysis(): UseWeaknessAnalysisReturn {
  const [analysis, setAnalysis] = useState<WeaknessAnalysisResponse | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchAnalysis = useCallback(
    async (testType: TestType = "ielts", limitAttempts: number = 5) => {
      setIsLoading(true)
      setError(null)

      try {
        const result = await analyzeWeakness({
          testType,
          limitAttempts,
        })
        setAnalysis(result)
      } catch (err) {
        const message = err instanceof Error ? err.message : "Analysis failed"
        setError(message)
        setAnalysis(null)
      } finally {
        setIsLoading(false)
      }
    },
    []
  )

  const fetchMockAnalysis = useCallback(async () => {
    setIsLoading(true)
    setError(null)

    try {
      const result = await getMockWeaknessAnalysis()
      setAnalysis(result)
    } catch (err) {
      const message = err instanceof Error ? err.message : "Analysis failed"
      setError(message)
      setAnalysis(null)
    } finally {
      setIsLoading(false)
    }
  }, [])

  const clearAnalysis = useCallback(() => {
    setAnalysis(null)
    setError(null)
  }, [])

  return {
    analysis,
    isLoading,
    error,
    fetchAnalysis,
    fetchMockAnalysis,
    clearAnalysis,
  }
}
