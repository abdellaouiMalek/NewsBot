"use client"

import { PageHeader } from "@/components/page-header"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { TrendingUp, Clock } from "lucide-react"
import { VoiceSummaryPlayer } from "@/components/voice-summary-player"
import { useState } from "react"

const trendingData = [
  { tag: "#AI", growth: "+45%", posts: "12.5K", trend: "up" },
  { tag: "#Climate", growth: "+32%", posts: "8.2K", trend: "up" },
  { tag: "#Elections", growth: "+28%", posts: "15.3K", trend: "up" },
  { tag: "#SpaceX", growth: "+18%", posts: "6.7K", trend: "up" },
  { tag: "#CyberSecurity", growth: "+52%", posts: "4.9K", trend: "up" },
  { tag: "#Blockchain", growth: "+38%", posts: "5.2K", trend: "up" },
]

const hourlyTrends = [
  { hour: "12:00 PM", trending: "#AI", momentum: "High" },
  { hour: "1:00 PM", trending: "#Elections", momentum: "Very High" },
  { hour: "2:00 PM", trending: "#Climate", momentum: "High" },
  { hour: "3:00 PM", trending: "#SpaceX", momentum: "Medium" },
]

export default function TrendsPage() {
  const [showVoicePlayer, setShowVoicePlayer] = useState(true)

  return (
    <div className="space-y-6">
      <PageHeader title="Trends" description="Real-time trending topics and emerging stories" />

      {showVoicePlayer && <VoiceSummaryPlayer trends={trendingData} onClose={() => setShowVoicePlayer(false)} />}

      {/* Top Trending Topics */}
      <div>
        <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <TrendingUp className="h-5 w-5 text-primary" />
          Top Trending Topics
        </h2>
        <div className="grid gap-4">
          {trendingData.map((item) => (
            <Card key={item.tag} className="hover:border-primary/50 transition-colors">
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <h3 className="font-semibold text-lg text-foreground">{item.tag}</h3>
                    <p className="text-sm text-muted-foreground mt-1">{item.posts} posts</p>
                  </div>
                  <div className="text-right">
                    <Badge className="bg-green-500/10 text-green-600 border-green-500/20 mb-2">{item.growth}</Badge>
                    <p className="text-xs text-muted-foreground">Growth</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>

      {/* Hourly Trends */}
      <div>
        <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Clock className="h-5 w-5 text-accent" />
          Hourly Trends
        </h2>
        <div className="grid gap-3">
          {hourlyTrends.map((item, index) => (
            <Card key={index}>
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-muted-foreground">{item.hour}</p>
                    <p className="font-semibold text-foreground mt-1">{item.trending}</p>
                  </div>
                  <Badge variant="outline">{item.momentum}</Badge>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </div>
  )
}
