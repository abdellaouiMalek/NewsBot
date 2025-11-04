"use client"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { TrustRatingIndicator } from "@/components/trust-rating-indicator"
import { AlertCircle, CheckCircle2, XCircle } from "lucide-react"

interface FactCheckingModalProps {
  isOpen: boolean
  onClose: () => void
  headline: string
  summary: string
  originalSource: string
}

interface SourceComparison {
  source: string
  headline: string
  summary: string
  trustScore: number
  credibility: "high" | "medium" | "low"
  factAccuracy: number
  biasLevel: "low" | "medium" | "high"
  reasoning: string
}

export function FactCheckingModal({ isOpen, onClose, headline, summary, originalSource }: FactCheckingModalProps) {
  // Mock data for fact-checking comparison
  const sourceComparisons: SourceComparison[] = [
    {
      source: originalSource,
      headline: headline,
      summary: summary,
      trustScore: 85,
      credibility: "high",
      factAccuracy: 88,
      biasLevel: "low",
      reasoning:
        "Established news organization with strong editorial standards. Story aligns with verified facts and includes multiple sources.",
    },
    {
      source: "Independent News Network",
      headline: "Breaking: Major Development in " + headline.split(":")[0],
      summary:
        "Similar story with additional context from alternative sources. Provides balanced perspective on the topic with independent verification.",
      trustScore: 72,
      credibility: "medium",
      factAccuracy: 75,
      biasLevel: "medium",
      reasoning:
        "Credible independent outlet with good track record. Story contains accurate information but includes some editorial interpretation.",
    },
    {
      source: "Global Wire Service",
      headline: headline.split(":")[0] + ": Full Analysis",
      summary:
        "Comprehensive coverage with international perspective. Includes expert commentary and historical context for better understanding.",
      trustScore: 78,
      credibility: "high",
      factAccuracy: 82,
      biasLevel: "low",
      reasoning:
        "International news agency with rigorous fact-checking process. Story is well-sourced and maintains journalistic integrity.",
    },
  ]

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-2xl">Fact Check Analysis</DialogTitle>
          <DialogDescription>
            Comparing the same story across multiple sources with AI-powered trust ratings
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6 mt-6">
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

          {/* Source Comparisons */}
          <div className="space-y-4">
            <h3 className="font-semibold text-lg">Source Comparison</h3>

            {sourceComparisons.map((comparison, index) => (
              <Card key={index} className="overflow-hidden">
                <CardHeader className="pb-3">
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1">
                      <CardTitle className="text-base mb-2">{comparison.source}</CardTitle>
                      <h4 className="font-medium text-sm mb-2">{comparison.headline}</h4>
                      <p className="text-sm text-muted-foreground">{comparison.summary}</p>
                    </div>
                    <TrustRatingIndicator score={comparison.trustScore} />
                  </div>
                </CardHeader>

                <CardContent className="space-y-4">
                  {/* Metrics */}
                  <div className="grid grid-cols-3 gap-4">
                    <div className="space-y-1">
                      <p className="text-xs text-muted-foreground font-medium">Fact Accuracy</p>
                      <div className="flex items-center gap-2">
                        <div className="flex-1 h-2 bg-secondary rounded-full overflow-hidden">
                          <div
                            className="h-full bg-primary transition-all"
                            style={{ width: `${comparison.factAccuracy}%` }}
                          />
                        </div>
                        <span className="text-sm font-semibold">{comparison.factAccuracy}%</span>
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
                          comparison.biasLevel === "low"
                            ? "bg-green-500/10 text-green-700 border-green-200"
                            : comparison.biasLevel === "medium"
                              ? "bg-yellow-500/10 text-yellow-700 border-yellow-200"
                              : "bg-red-500/10 text-red-700 border-red-200"
                        }
                      >
                        {comparison.biasLevel.charAt(0).toUpperCase() + comparison.biasLevel.slice(1)}
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

          {/* Summary */}
          <Card className="bg-primary/5 border-primary/20">
            <CardHeader>
              <CardTitle className="text-base">Overall Assessment</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2 text-sm">
              <p>
                This story is covered consistently across multiple reputable sources with high fact accuracy. The core
                claims are well-supported by evidence and expert commentary.
              </p>
              <p className="text-muted-foreground">
                <strong>Recommendation:</strong> This article is reliable for understanding the topic. All sources
                maintain journalistic integrity with minimal bias.
              </p>
            </CardContent>
          </Card>
        </div>
      </DialogContent>
    </Dialog>
  )
}
