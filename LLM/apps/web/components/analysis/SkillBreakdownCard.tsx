"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@workspace/ui/components/card"
import { Badge } from "@workspace/ui/components/badge"
import { Progress } from "@workspace/ui/components/progress"
import { SkillBreakdown } from "@/lib/api"
import { BookOpen, Headphones, PenTool, Mic } from "lucide-react"

interface SkillBreakdownCardProps {
  breakdown: SkillBreakdown[]
}

const skillIcons = {
  reading: BookOpen,
  listening: Headphones,
  writing: PenTool,
  speaking: Mic,
}

const skillColors = {
  reading: "bg-blue-500",
  listening: "bg-green-500",
  writing: "bg-purple-500",
  speaking: "bg-orange-500",
}

export function SkillBreakdownCard({ breakdown }: SkillBreakdownCardProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">Skills Breakdown</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {breakdown.map((skill) => {
          const Icon = skillIcons[skill.skill] || BookOpen
          const colorClass = skillColors[skill.skill] || "bg-gray-500"
          
          return (
            <div key={skill.skill} className="space-y-2">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Icon className="h-4 w-4 text-muted-foreground" />
                  <span className="font-medium capitalize">{skill.skill}</span>
                </div>
                <span className="text-sm text-muted-foreground">
                  {skill.wrongCount}/{skill.totalCount} wrong ({skill.errorRate}%)
                </span>
              </div>
              
              <Progress 
                value={100 - skill.errorRate} 
                className="h-2"
              />
              
              {skill.weakTags.length > 0 && (
                <div className="flex flex-wrap gap-1">
                  {skill.weakTags.map((tag) => (
                    <Badge key={tag} variant="secondary" className="text-xs">
                      {tag}
                    </Badge>
                  ))}
                </div>
              )}
            </div>
          )
        })}
        
        {breakdown.length === 0 && (
          <p className="text-sm text-muted-foreground">No skill data available.</p>
        )}
      </CardContent>
    </Card>
  )
}
