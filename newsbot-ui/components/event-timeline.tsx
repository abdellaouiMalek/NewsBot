"use client"

import { useState } from "react"
import { ChevronDown } from "lucide-react"
import { cn } from "@/lib/utils"

interface TimelineEvent {
  id: number
  title: string
  description: string
  category: string
}

interface TimelinePoint {
  date: string
  title: string
  summary: string
  details: string
  impact: string
}

const eventTimelines: Record<number, TimelinePoint[]> = {
  1: [
    {
      date: "Oct 7, 2023",
      title: "Hamas Attack",
      summary: "Major military operation launched against Israel",
      details:
        "Hamas launched a coordinated attack on Israel, resulting in significant casualties and hostages taken. This marked a major escalation in the long-standing conflict.",
      impact: "High - Triggered immediate military response and international attention",
    },
    {
      date: "Oct 9, 2023",
      title: "Israeli Response",
      summary: "Israel declares war and begins military operations",
      details:
        "Israel declared war on Hamas and began extensive military operations in Gaza. The response included airstrikes and ground operations.",
      impact: "High - Escalated conflict to full-scale military engagement",
    },
    {
      date: "Oct 15, 2023",
      title: "Humanitarian Crisis",
      summary: "Civilian casualties and displacement reported",
      details:
        "Reports of significant civilian casualties and displacement of populations. International humanitarian organizations called for ceasefire.",
      impact: "Critical - Humanitarian concerns raised globally",
    },
    {
      date: "Nov 1, 2023",
      title: "International Involvement",
      summary: "Global powers engage in diplomatic efforts",
      details:
        "Various international bodies and countries attempted diplomatic interventions. UN called for humanitarian corridors.",
      impact: "Medium - Diplomatic pressure increased",
    },
    {
      date: "Dec 1, 2023",
      title: "Ceasefire Negotiations",
      summary: "Talks for temporary ceasefire begin",
      details:
        "Initial ceasefire negotiations began with international mediation. Humanitarian aid started flowing into affected areas.",
      impact: "Medium - Temporary relief for civilians",
    },
    {
      date: "Jan 15, 2024",
      title: "Ongoing Tensions",
      summary: "Conflict continues with periodic escalations",
      details: "Despite negotiations, sporadic violence continued. Reconstruction efforts began in some areas.",
      impact: "Medium - Situation remains volatile",
    },
  ],
  2: [
    {
      date: "Jan 2024",
      title: "Record Temperatures",
      summary: "Global temperatures reach new highs",
      details: "2024 started with record-breaking temperatures across multiple continents, breaking previous records.",
      impact: "High - Climate emergency declared",
    },
    {
      date: "Mar 2024",
      title: "Extreme Weather Events",
      summary: "Increased frequency of severe weather",
      details: "Multiple hurricanes, floods, and droughts reported worldwide affecting millions.",
      impact: "Critical - Humanitarian impact",
    },
    {
      date: "Jun 2024",
      title: "Climate Summit",
      summary: "Global leaders meet to discuss climate action",
      details: "International climate conference focused on emission reduction targets and green energy transition.",
      impact: "Medium - Policy discussions ongoing",
    },
  ],
  3: [
    {
      date: "Jan 2024",
      title: "GPT-5 Release",
      summary: "Advanced AI model released",
      details:
        "New generation of AI models with improved capabilities launched, showing significant improvements in reasoning.",
      impact: "High - Industry transformation",
    },
    {
      date: "Mar 2024",
      title: "AI Regulation",
      summary: "Governments propose AI regulation frameworks",
      details: "Multiple countries announced regulatory frameworks for AI development and deployment.",
      impact: "Medium - Policy development",
    },
    {
      date: "Jun 2024",
      title: "AI in Healthcare",
      summary: "AI applications approved for medical use",
      details: "Several AI diagnostic tools received regulatory approval for clinical use.",
      impact: "High - Healthcare transformation",
    },
  ],
  4: [
    {
      date: "Jan 2024",
      title: "Market Volatility",
      summary: "Stock markets experience significant fluctuations",
      details: "Global markets showed volatility due to interest rate concerns and geopolitical tensions.",
      impact: "Medium - Investor caution",
    },
    {
      date: "Apr 2024",
      title: "Tech Sector Boom",
      summary: "Technology stocks surge on AI optimism",
      details: "Tech companies saw significant growth driven by AI and cloud computing investments.",
      impact: "High - Market rally",
    },
    {
      date: "Jul 2024",
      title: "Economic Slowdown",
      summary: "Growth rates decline in major economies",
      details: "Several major economies reported slower growth rates, raising recession concerns.",
      impact: "Medium - Economic uncertainty",
    },
  ],
}

interface EventTimelineProps {
  event: TimelineEvent
}

export function EventTimeline({ event }: EventTimelineProps) {
  const [expandedId, setExpandedId] = useState<number | null>(0)
  const timeline = eventTimelines[event.id] || []

  return (
    <div className="space-y-6">
      <div className="bg-card border border-border rounded-lg p-6">
        <h2 className="text-2xl font-bold text-foreground">{event.title}</h2>
        <p className="text-muted-foreground mt-2">{event.description}</p>
      </div>

      {/* Timeline */}
      <div className="relative">
        {/* Vertical line */}
        <div className="absolute left-6 top-0 bottom-0 w-0.5 bg-gradient-to-b from-primary to-primary/20" />

        {/* Timeline items */}
        <div className="space-y-4">
          {timeline.map((point, index) => (
            <div key={index} className="relative pl-20">
              {/* Timeline dot */}
              <div className="absolute left-0 top-2 w-12 h-12 flex items-center justify-center">
                <div className="w-4 h-4 rounded-full bg-primary border-4 border-background" />
              </div>

              {/* Timeline card */}
              <button
                onClick={() => setExpandedId(expandedId === index ? null : index)}
                className={cn(
                  "w-full text-left p-4 rounded-lg border transition-all",
                  expandedId === index
                    ? "bg-primary/5 border-primary"
                    : "bg-card border-border hover:border-primary/50",
                )}
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-semibold text-primary">{point.date}</span>
                      <span className="text-xs px-2 py-1 rounded-full bg-primary/10 text-primary">
                        {point.impact.split(" - ")[0]}
                      </span>
                    </div>
                    <h3 className="font-semibold text-foreground mt-2">{point.title}</h3>
                    <p className="text-sm text-muted-foreground mt-1">{point.summary}</p>
                  </div>
                  <ChevronDown
                    className={cn(
                      "h-5 w-5 text-muted-foreground transition-transform flex-shrink-0",
                      expandedId === index && "transform rotate-180",
                    )}
                  />
                </div>

                {/* Expanded details */}
                {expandedId === index && (
                  <div className="mt-4 pt-4 border-t border-border space-y-3">
                    <div>
                      <h4 className="text-sm font-semibold text-foreground mb-1">Details</h4>
                      <p className="text-sm text-muted-foreground">{point.details}</p>
                    </div>
                    <div>
                      <h4 className="text-sm font-semibold text-foreground mb-1">Impact</h4>
                      <p className="text-sm text-muted-foreground">{point.impact}</p>
                    </div>
                  </div>
                )}
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Timeline stats */}
      <div className="grid grid-cols-3 gap-4 mt-8">
        <div className="bg-card border border-border rounded-lg p-4 text-center">
          <div className="text-2xl font-bold text-primary">{timeline.length}</div>
          <div className="text-xs text-muted-foreground mt-1">Key Events</div>
        </div>
        <div className="bg-card border border-border rounded-lg p-4 text-center">
          <div className="text-2xl font-bold text-primary">
            {timeline.filter((p) => p.impact.includes("High") || p.impact.includes("Critical")).length}
          </div>
          <div className="text-xs text-muted-foreground mt-1">Major Events</div>
        </div>
        <div className="bg-card border border-border rounded-lg p-4 text-center">
          <div className="text-2xl font-bold text-primary">{new Date().getFullYear() - 2023}</div>
          <div className="text-xs text-muted-foreground mt-1">Years Tracked</div>
        </div>
      </div>
    </div>
  )
}
