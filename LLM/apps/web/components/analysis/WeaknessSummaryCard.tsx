"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@workspace/ui/components/card"
import { AlertCircle, Lightbulb } from "lucide-react"

interface WeaknessSummaryCardProps {
  description: string
  suggestions: string[]
}

export function WeaknessSummaryCard({ description, suggestions }: WeaknessSummaryCardProps) {
  return (
    <div className="space-y-4">
      {/* Weakness Description */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center gap-2 text-lg">
            <AlertCircle className="h-5 w-5 text-orange-500" />
            Weakness Analysis
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground leading-relaxed">
            {description || "No weakness description available."}
          </p>
        </CardContent>
      </Card>

      {/* Improvement Suggestions */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center gap-2 text-lg">
            <Lightbulb className="h-5 w-5 text-yellow-500" />
            Improvement Suggestions
          </CardTitle>
        </CardHeader>
        <CardContent>
          {suggestions.length > 0 ? (
            <ol className="space-y-3 list-decimal list-inside">
              {suggestions.map((suggestion, index) => (
                <li key={index} className="text-muted-foreground leading-relaxed">
                  <span className="ml-1">{suggestion}</span>
                </li>
              ))}
            </ol>
          ) : (
            <p className="text-muted-foreground">No suggestions available.</p>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
