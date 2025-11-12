"use client"

import { FactCheckingModal } from "@/components/fact-checking-modal"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardFooter, CardHeader } from "@/components/ui/card"
import { usePreferences } from "@/lib/preferences-hook"
import { stripHtml } from "@/lib/utils"
import { Clock, ExternalLink, ShieldCheck, ThumbsDown, ThumbsUp } from "lucide-react"
import { useState } from "react"

interface NewsCardProps {
  id?: number
  articleId?: string
  headline: string
  summary: string
  source: string
  time: string
  category: string
}

export function NewsCard({ id = 1, articleId, headline, summary, source, time, category }: NewsCardProps) {
  const [isFactCheckOpen, setIsFactCheckOpen] = useState(false)
  const [feedbackGiven, setFeedbackGiven] = useState(false)
  const { addFeedback } = usePreferences()

  // Strip any HTML that might come from the backend for safe display
  const safeHeadline = stripHtml(headline);
  const safeSummary = stripHtml(summary);

  const handleFeedback = (rating: "like" | "dislike", relevant: boolean) => {
    addFeedback(id, safeHeadline, category, rating, relevant)
    setFeedbackGiven(true)
    setTimeout(() => setFeedbackGiven(false), 2000)
  }

  return (
    <>
      <Card className="group hover:shadow-lg transition-all duration-300 hover:border-primary/50 w-full">
        <CardHeader className="space-y-2 md:space-y-3 p-4 md:p-6">
          <div className="flex items-start justify-between gap-2 md:gap-4">
              <h3 className="text-lg md:text-xl font-semibold leading-tight group-hover:text-primary transition-colors text-balance">
              {safeHeadline}
            </h3>
            {/* <Badge
              variant="secondary"
              className="shrink-0 bg-primary/10 text-primary border-primary/20 text-xs md:text-sm"
            >
              <Sparkles className="h-3 w-3 mr-1" />
              AI
            </Badge> */}
          </div>
        </CardHeader>

        <CardContent className="p-4 md:p-6 pt-0 md:pt-0">
          <p className="text-sm md:text-base text-muted-foreground leading-relaxed text-pretty">
            {stripHtml(summary)}
          </p>
        </CardContent>

        <CardFooter className="flex flex-col md:flex-row items-start md:items-center justify-between gap-3 md:gap-0 p-4 md:p-6 pt-0 md:pt-0">
          <div className="flex items-center justify-between gap-2 md:gap-4 text-xs md:text-sm text-muted-foreground w-full">
            <div className="flex items-center gap-2 md:gap-4">
              <span className="font-medium">{source}</span>
              <div className="flex items-center gap-1">
                <Clock className="h-3.5 w-3.5" />
                <span>{time}</span>
              </div>
            </div>
            {feedbackGiven && <span className="text-xs text-primary font-medium">Feedback saved</span>}
          </div>

          <div className="flex flex-col md:flex-row gap-2 w-full">
            <div className="flex gap-2 flex-1">
              <Button
                variant="ghost"
                size="sm"
                className="gap-2 text-xs md:text-sm flex-1 md:flex-none"
                onClick={() => handleFeedback("like", true)}
                title="Mark as helpful"
              >
                <ThumbsUp className="h-4 w-4" />
                <span className="hidden sm:inline">Helpful</span>
              </Button>
              <Button
                variant="ghost"
                size="sm"
                className="gap-2 text-xs md:text-sm flex-1 md:flex-none"
                onClick={() => handleFeedback("dislike", false)}
                title="Mark as not helpful"
              >
                <ThumbsDown className="h-4 w-4" />
                <span className="hidden sm:inline">Not Helpful</span>
              </Button>
            </div>

            <Button
              variant="ghost"
              size="sm"
              className="gap-2 text-xs md:text-sm"
              onClick={() => setIsFactCheckOpen(true)}
            >
              <ShieldCheck className="h-4 w-4" />
              Fact Check
            </Button>

            <Button variant="ghost" size="sm" className="gap-2 text-xs md:text-sm">
              Read More
              <ExternalLink className="h-4 w-4" />
            </Button>
          </div>
        </CardFooter>
      </Card>

      <FactCheckingModal
        isOpen={isFactCheckOpen}
        onClose={() => setIsFactCheckOpen(false)}
        articleId={articleId || ""}
        headline={safeHeadline}
        summary={safeSummary}
        originalSource={source}
      />
    </>
  )
}
