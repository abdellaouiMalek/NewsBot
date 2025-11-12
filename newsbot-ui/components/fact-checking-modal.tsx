"use client"
import { TrustRatingIndicator } from "@/components/trust-rating-indicator"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { SourceComparison, useFactCheck } from "@/lib/api"
import { AlertCircle, CheckCircle2, Loader2, XCircle } from "lucide-react"
import { useEffect, useState } from "react"

interface FactCheckingModalProps {
  isOpen: boolean
  onClose: () => void
  articleId: string
  headline: string
  summary: string
  originalSource: string
}

export function FactCheckingModal({ isOpen, onClose, articleId, headline, summary, originalSource }: FactCheckingModalProps) {
  const factCheckMutation = useFactCheck()
  const [sourceComparisons, setSourceComparisons] = useState<SourceComparison[]>([])
  const [overallAssessment, setOverallAssessment] = useState("")
  const [recommendation, setRecommendation] = useState("")
  const [totalSourcesFound, setTotalSourcesFound] = useState(0)

  // Trigger fact-check when modal opens
  useEffect(() => {
    if (isOpen && articleId) {
      // Reset state
      setSourceComparisons([])
      setOverallAssessment("")
      setRecommendation("")
      setTotalSourcesFound(0)

      // Call fact-check API
      factCheckMutation.mutate(
        {
          article_id: articleId,
          headline,
          summary,
          source: originalSource,
        },
        {
          onSuccess: (data) => {
            setSourceComparisons(data.comparisons)
            setOverallAssessment(data.overall_assessment)
            setRecommendation(data.recommendation)
            setTotalSourcesFound(data.total_sources_found)
          },
          onError: (error) => {
            console.error("Fact-check error:", error)
          },
        }
      )
    }
  }, [isOpen, articleId])

  const isLoading = factCheckMutation.isPending
  const isError = factCheckMutation.isError

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-[90hw] max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-2xl">Fact Check Analysis</DialogTitle>
          <DialogDescription>
            Comparing the same story across multiple sources with AI-powered trust ratings
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6 mt-6">
          {/* Loading State */}
          {isLoading && (
            <div className="flex flex-col items-center justify-center py-12 space-y-4">
              <Loader2 className="h-8 w-8 animate-spin text-primary" />
              <div className="text-center space-y-2">
                <p className="text-sm font-medium text-foreground">
                  Performing AI-powered fact-check...
                </p>
                <p className="text-xs text-muted-foreground">
                  This may take 3-5 minutes. We're:
                </p>
                <ul className="text-xs text-muted-foreground space-y-1 text-left max-w-md mx-auto">
                  <li>• Searching 15 similar articles using AI embeddings</li>
                  <li>• Asking AI to identify articles about the same story</li>
                  <li>• Analyzing each source for credibility and bias</li>
                  <li>• Generating comprehensive assessment</li>
                </ul>
              </div>
            </div>
          )}

          {/* Error State */}
          {isError && (
            <Card className="bg-destructive/10 border-destructive/20">
              <CardContent className="pt-6 space-y-2">
                <p className="text-sm text-destructive font-medium">
                  Failed to perform fact-check
                </p>
                <p className="text-xs text-muted-foreground">
                  {factCheckMutation.error instanceof Error && 
                   factCheckMutation.error.message.includes('timeout')
                    ? 'The analysis took longer than expected. This can happen with complex articles or when the AI is busy. Please try again.'
                    : 'An error occurred while analyzing the article. Please try again later.'}
                </p>
              </CardContent>
            </Card>
          )}

          {/* Results */}
          {!isLoading && !isError && (
            <>
              {/* Original Article Summary */}
              <Card className="bg-card/50 border-primary/20">
                <CardHeader>
                  <CardTitle className="text-lg">Original Article</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <h3 className="font-semibold text-base">{headline}</h3>
                  <p className="text-sm text-muted-foreground">{summary}</p>
                  <Badge variant="outline">{originalSource}</Badge>
                </CardContent>
              </Card>

              {/* No sources found message */}
              {totalSourcesFound === 0 && (
                <Card className="bg-secondary/20 border-secondary">
                  <CardContent className="pt-6">
                    <p className="text-sm text-muted-foreground">
                      No similar articles from other sources were found in the database.
                      Unable to perform comparative fact-checking at this time.
                    </p>
                  </CardContent>
                </Card>
              )}

              {/* Source Comparisons */}
              {sourceComparisons.length > 0 && (
                <div className="space-y-4">
                  <h3 className="font-semibold text-lg">
                    Source Comparison ({totalSourcesFound} {totalSourcesFound === 1 ? 'source' : 'sources'} found)
                  </h3>

                  <div className="flex gap-4 overflow-x-auto pb-4 snap-x snap-mandatory">
                    {sourceComparisons.map((comparison, index) => (
                      <Card key={index} className="overflow-hidden flex-none w-[400px] snap-start">
                        <CardHeader className="pb-3">
                          <div className="flex flex-col gap-3">
                            <div className="flex items-start justify-between gap-2">
                              <CardTitle className="text-base flex-1">{comparison.source}</CardTitle>
                              <TrustRatingIndicator score={comparison.trust_score} />
                            </div>
                            <h4 className="font-medium text-sm">{comparison.headline}</h4>
                            <p className="text-sm text-muted-foreground line-clamp-3">{comparison.summary}</p>
                          </div>
                        </CardHeader>

                        <CardContent className="space-y-4">
                          {/* Metrics */}
                          <div className="space-y-3">
                            <div className="space-y-1">
                              <p className="text-xs text-muted-foreground font-medium">Fact Accuracy</p>
                              <div className="flex items-center gap-2">
                                <div className="flex-1 h-2 bg-secondary rounded-full overflow-hidden">
                                  <div
                                    className="h-full bg-primary transition-all"
                                    style={{ width: `${comparison.fact_accuracy}%` }}
                                  />
                                </div>
                                <span className="text-sm font-semibold">{comparison.fact_accuracy}%</span>
                              </div>
                            </div>

                            <div className="space-y-1">
                              <p className="text-xs text-muted-foreground font-medium">Credibility</p>
                              <div className="flex items-center gap-2">
                                {comparison.credibility === "high" && <CheckCircle2 className="h-4 w-4 text-green-500" />}
                                {comparison.credibility === "medium" && <AlertCircle className="h-4 w-4 text-yellow-500" />}
                                {comparison.credibility === "low" && <XCircle className="h-4 w-4 text-red-500" />}
                                <Badge
                                  variant="outline"
                                  className={
                                    comparison.credibility === "high"
                                      ? "bg-green-500/10 text-green-700 border-green-200"
                                      : comparison.credibility === "medium"
                                        ? "bg-yellow-500/10 text-yellow-700 border-yellow-200"
                                        : "bg-red-500/10 text-red-700 border-red-200"
                                  }
                                >
                                  {comparison.credibility.charAt(0).toUpperCase() + comparison.credibility.slice(1)}
                                </Badge>
                              </div>
                            </div>

                            <div className="space-y-1">
                              <p className="text-xs text-muted-foreground font-medium">Bias Level</p>
                              <Badge
                                variant="outline"
                                className={
                                  comparison.bias_level === "low"
                                    ? "bg-green-500/10 text-green-700 border-green-200"
                                    : comparison.bias_level === "medium"
                                      ? "bg-yellow-500/10 text-yellow-700 border-yellow-200"
                                      : "bg-red-500/10 text-red-700 border-red-200"
                                }
                              >
                                {comparison.bias_level.charAt(0).toUpperCase() + comparison.bias_level.slice(1)}
                              </Badge>
                            </div>
                          </div>

                          {/* AI Reasoning */}
                          <div className="bg-secondary/30 rounded-lg p-3 border border-secondary">
                            <p className="text-xs font-semibold text-muted-foreground mb-1">AI Analysis</p>
                            <p className="text-sm text-foreground">{comparison.reasoning}</p>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                </div>
              )}

              {/* Summary */}
              {overallAssessment && (
                <Card className="bg-primary/5 border-primary/20">
                  <CardHeader>
                    <CardTitle className="text-base">Overall Assessment</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-2 text-sm">
                    <p>{overallAssessment}</p>
                    {recommendation && (
                      <p className="text-muted-foreground">
                        <strong>Recommendation:</strong> {recommendation}
                      </p>
                    )}
                  </CardContent>
                </Card>
              )}
            </>
          )}
        </div>
      </DialogContent>
    </Dialog>
  )
}
