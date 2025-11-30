"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@workspace/ui/components/card"
import { Button } from "@workspace/ui/components/button"
import { Badge } from "@workspace/ui/components/badge"
import { GeneratedQuestion } from "@/lib/api"
import { CheckCircle, XCircle, ChevronDown, ChevronUp, Target } from "lucide-react"

interface PracticeQuestionsCardProps {
  questions: GeneratedQuestion[]
}

export function PracticeQuestionsCard({ questions }: PracticeQuestionsCardProps) {
  const [expandedId, setExpandedId] = useState<string | null>(null)
  const [answers, setAnswers] = useState<Record<string, string>>({})
  const [showResults, setShowResults] = useState<Record<string, boolean>>({})

  const handleAnswer = (questionId: string, answer: string) => {
    setAnswers((prev) => ({ ...prev, [questionId]: answer }))
  }

  const checkAnswer = (questionId: string) => {
    setShowResults((prev) => ({ ...prev, [questionId]: true }))
  }

  const isCorrect = (question: GeneratedQuestion, answer: string) => {
    const normalizedAnswer = answer.trim().toLowerCase()
    return question.correctAnswer.some(
      (correct) => correct.toLowerCase() === normalizedAnswer
    )
  }

  const toggleExpand = (questionId: string) => {
    setExpandedId(expandedId === questionId ? null : questionId)
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-lg">
          <Target className="h-5 w-5 text-blue-500" />
          Practice Questions ({questions.length})
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {questions.length === 0 ? (
          <p className="text-muted-foreground">No practice questions generated.</p>
        ) : (
          questions.map((question, index) => (
            <div
              key={question.id}
              className="border rounded-lg p-4 space-y-3"
            >
              {/* Question Header */}
              <div className="flex items-start justify-between gap-2">
                <div className="space-y-1 flex-1">
                  <div className="flex items-center gap-2">
                    <span className="font-medium">Q{index + 1}.</span>
                    <Badge variant="secondary" className="text-xs">
                      {question.type}
                    </Badge>
                    <Badge variant="outline" className="text-xs capitalize">
                      {question.difficulty}
                    </Badge>
                  </div>
                  <p className="text-sm">{question.content}</p>
                </div>
              </div>

              {/* Tags */}
              <div className="flex flex-wrap gap-1">
                {question.targetTags.map((tag) => (
                  <Badge key={tag} variant="secondary" className="text-xs">
                    {tag}
                  </Badge>
                ))}
              </div>

              {/* Options for Multiple Choice */}
              {question.type === "multiple-choice" && question.options && (
                <div className="space-y-2">
                  {question.options.map((option, optIndex) => {
                    const optionLetter = option.charAt(0)
                    const isSelected = answers[question.id] === optionLetter
                    const hasResult = showResults[question.id]
                    const isOptionCorrect = question.correctAnswer.includes(optionLetter)

                    let optionClass = "border rounded-md p-2 cursor-pointer text-sm transition-colors"
                    if (hasResult) {
                      if (isOptionCorrect) {
                        optionClass += " bg-green-100 border-green-500 dark:bg-green-900/30"
                      } else if (isSelected && !isOptionCorrect) {
                        optionClass += " bg-red-100 border-red-500 dark:bg-red-900/30"
                      }
                    } else if (isSelected) {
                      optionClass += " bg-primary/10 border-primary"
                    } else {
                      optionClass += " hover:bg-accent"
                    }

                    return (
                      <div
                        key={optIndex}
                        className={optionClass}
                        onClick={() => !hasResult && handleAnswer(question.id, optionLetter)}
                      >
                        {option}
                      </div>
                    )
                  })}
                </div>
              )}

              {/* Fill in the Blank Input */}
              {question.type === "fill-blank" && (
                <div className="flex gap-2">
                  <input
                    type="text"
                    placeholder="Type your answer..."
                    className="flex-1 px-3 py-2 border rounded-md text-sm"
                    value={answers[question.id] || ""}
                    onChange={(e) => handleAnswer(question.id, e.target.value)}
                    disabled={showResults[question.id]}
                  />
                </div>
              )}

              {/* Check/Result Button */}
              <div className="flex items-center gap-2">
                {!showResults[question.id] ? (
                  <Button
                    size="sm"
                    onClick={() => checkAnswer(question.id)}
                    disabled={!answers[question.id]}
                  >
                    Check Answer
                  </Button>
                ) : (
                  <div className="flex items-center gap-2">
                    {isCorrect(question, answers[question.id] || "") ? (
                      <>
                        <CheckCircle className="h-5 w-5 text-green-500" />
                        <span className="text-green-600 font-medium">Correct!</span>
                      </>
                    ) : (
                      <>
                        <XCircle className="h-5 w-5 text-red-500" />
                        <span className="text-red-600 font-medium">
                          Incorrect. Answer: {question.correctAnswer.join(", ")}
                        </span>
                      </>
                    )}
                  </div>
                )}

                {/* Expand/Collapse Explanation */}
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => toggleExpand(question.id)}
                  className="ml-auto"
                >
                  {expandedId === question.id ? (
                    <>
                      Hide Explanation <ChevronUp className="h-4 w-4 ml-1" />
                    </>
                  ) : (
                    <>
                      Show Explanation <ChevronDown className="h-4 w-4 ml-1" />
                    </>
                  )}
                </Button>
              </div>

              {/* Explanation */}
              {expandedId === question.id && (
                <div className="bg-muted/50 rounded-md p-3 text-sm text-muted-foreground">
                  <strong>Explanation:</strong> {question.explanation}
                </div>
              )}
            </div>
          ))
        )}
      </CardContent>
    </Card>
  )
}
