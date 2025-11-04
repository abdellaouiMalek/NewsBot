"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { TrendingUp, Zap } from "lucide-react"
import { cn } from "@/lib/utils"

const trendingTopics = [
  { tag: "#AI", count: "12.5K posts" },
  { tag: "#Climate", count: "8.2K posts" },
  { tag: "#Elections", count: "15.3K posts" },
  { tag: "#SpaceX", count: "6.7K posts" },
  { tag: "#CyberSecurity", count: "4.9K posts" },
]

const liveUpdates = [
  { title: "Breaking: Major tech company announces acquisition", time: "2m ago" },
  { title: "Markets respond to Federal Reserve decision", time: "15m ago" },
  { title: "International summit begins in Geneva", time: "32m ago" },
  { title: "New study reveals surprising health findings", time: "1h ago" },
]

export function RightSidebar() {
  const [viewMode, setViewMode] = useState<"brief" | "detailed">("brief")

  return (
    <aside className="w-80 border-l border-border bg-card p-6 space-y-6 overflow-y-auto">
      {/* Trending Topics */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-lg">
            <TrendingUp className="h-5 w-5 text-primary" />
            Trending Topics
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {trendingTopics.map((topic) => (
            <button
              key={topic.tag}
              className="w-full flex items-center justify-between p-3 rounded-lg hover:bg-accent transition-colors text-left group"
            >
              <span className="font-medium text-foreground group-hover:text-primary transition-colors">
                {topic.tag}
              </span>
              <span className="text-xs text-muted-foreground">{topic.count}</span>
            </button>
          ))}
        </CardContent>
      </Card>

      {/* Live Updates */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2 text-lg">
              <Zap className="h-5 w-5 text-accent" />
              Live Updates
            </CardTitle>
            <Badge variant="outline" className="animate-pulse">
              Live
            </Badge>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          {liveUpdates.map((update, index) => (
            <div key={index} className="pb-4 border-b border-border last:border-0 last:pb-0 group cursor-pointer">
              <p className="text-sm font-medium leading-snug group-hover:text-primary transition-colors text-balance">
                {update.title}
              </p>
              <p className="text-xs text-muted-foreground mt-1">{update.time}</p>
            </div>
          ))}
        </CardContent>
      </Card>

      {/* View Mode Toggle */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">View Preference</CardTitle>
        </CardHeader>
        <CardContent className="flex gap-2">
          <Button
            variant={viewMode === "brief" ? "default" : "outline"}
            className={cn("flex-1", viewMode === "brief" && "bg-primary")}
            onClick={() => setViewMode("brief")}
          >
            Brief
          </Button>
          <Button
            variant={viewMode === "detailed" ? "default" : "outline"}
            className={cn("flex-1", viewMode === "detailed" && "bg-primary")}
            onClick={() => setViewMode("detailed")}
          >
            Detailed
          </Button>
        </CardContent>
      </Card>
    </aside>
  )
}
