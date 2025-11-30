"use client"

import { Button } from "@workspace/ui/components/button"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@workspace/ui/components/card"
import { Alert, AlertDescription } from "@workspace/ui/components/alert"
import { useWeaknessAnalysis } from "@/hooks/useWeaknessAnalysis"
import { SkillBreakdownCard } from "./SkillBreakdownCard"
import { WeaknessSummaryCard } from "./WeaknessSummaryCard"
import { PracticeQuestionsCard } from "./PracticeQuestionsCard"
import { Loader2, Brain, BarChart3, RefreshCw } from "lucide-react"

export function AnalysisDashboard() {
  const { analysis, isLoading, error, fetchMockAnalysis, clearAnalysis } = useWeaknessAnalysis()

  const formatDate = (timestamp: number) => {
    return new Date(timestamp).toLocaleString()
  }

  return (
    <div className="container mx-auto py-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2">
            <Brain className="h-6 w-6" />
            Weakness Analysis
          </h1>
          <p className="text-muted-foreground">
            Analyze your test history to identify areas for improvement
          </p>
        </div>

        <div className="flex gap-2">
          {analysis && (
            <Button variant="outline" onClick={clearAnalysis}>
              Clear
            </Button>
          )}
          <Button onClick={fetchMockAnalysis} disabled={isLoading}>
            {isLoading ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin mr-2" />
                Analyzing...
              </>
            ) : (
              <>
                <RefreshCw className="h-4 w-4 mr-2" />
                {analysis ? "Re-analyze" : "Start Analysis"}
              </>
            )}
          </Button>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Initial State */}
      {!analysis && !isLoading && !error && (
        <Card className="border-dashed">
          <CardContent className="flex flex-col items-center justify-center py-12">
            <BarChart3 className="h-12 w-12 text-muted-foreground mb-4" />
            <CardTitle className="mb-2">No Analysis Yet</CardTitle>
            <CardDescription className="text-center max-w-md mb-4">
              Click "Start Analysis" to analyze your last 5 test attempts and get 
              personalized insights and practice questions.
            </CardDescription>
            <Button onClick={fetchMockAnalysis}>
              <Brain className="h-4 w-4 mr-2" />
              Start Analysis
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Loading State */}
      {isLoading && (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <Loader2 className="h-12 w-12 animate-spin text-primary mb-4" />
            <p className="text-muted-foreground">Analyzing your test history...</p>
            <p className="text-sm text-muted-foreground">This may take a few seconds</p>
          </CardContent>
        </Card>
      )}

      {/* Analysis Results */}
      {analysis && !isLoading && (
        <div className="space-y-6">
          {/* Summary Stats */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card>
              <CardHeader className="pb-2">
                <CardDescription>Test Type</CardDescription>
                <CardTitle className="text-2xl uppercase">{analysis.testType}</CardTitle>
              </CardHeader>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardDescription>Questions Analyzed</CardDescription>
                <CardTitle className="text-2xl">{analysis.totalQuestionsAnalyzed}</CardTitle>
              </CardHeader>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardDescription>Wrong Answers</CardDescription>
                <CardTitle className="text-2xl text-red-500">{analysis.totalWrongAnswers}</CardTitle>
              </CardHeader>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardDescription>Analyzed At</CardDescription>
                <CardTitle className="text-lg">{formatDate(analysis.analyzedAt)}</CardTitle>
              </CardHeader>
            </Card>
          </div>

          {/* Main Content Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Left Column - Skills Breakdown */}
            <div className="lg:col-span-1">
              <SkillBreakdownCard breakdown={analysis.skillBreakdown} />
            </div>

            {/* Right Column - Weakness & Suggestions */}
            <div className="lg:col-span-2">
              <WeaknessSummaryCard
                description={analysis.weaknessDescription}
                suggestions={analysis.improvementSuggestions}
              />
            </div>
          </div>

          {/* Practice Questions - Full Width */}
          <PracticeQuestionsCard questions={analysis.practiceQuestions} />
        </div>
      )}
    </div>
  )
}
