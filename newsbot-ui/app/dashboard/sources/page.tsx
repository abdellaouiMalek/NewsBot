"use client"

import { useState } from "react"
import { PageHeader } from "@/components/page-header"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { Search, Star, Trash2 } from "lucide-react"

const sources = [
  { name: "TechCrunch", category: "Technology", followers: "2.3M", reliability: "High" },
  { name: "Reuters", category: "General News", followers: "5.1M", reliability: "Very High" },
  { name: "Bloomberg", category: "Business", followers: "3.8M", reliability: "Very High" },
  { name: "Nature", category: "Science", followers: "1.2M", reliability: "Very High" },
  { name: "ESPN", category: "Sports", followers: "4.2M", reliability: "High" },
  { name: "The Verge", category: "Technology", followers: "1.8M", reliability: "High" },
]

export default function SourcesPage() {
  const [followedSources, setFollowedSources] = useState<string[]>(["TechCrunch", "Reuters"])
  const [searchQuery, setSearchQuery] = useState("")

  const toggleSource = (sourceName: string) => {
    setFollowedSources((prev) =>
      prev.includes(sourceName) ? prev.filter((s) => s !== sourceName) : [...prev, sourceName],
    )
  }

  const filteredSources = sources.filter((source) => source.name.toLowerCase().includes(searchQuery.toLowerCase()))

  return (
    <div className="space-y-6">
      <PageHeader title="Sources" description="Manage your news sources and customize your information diet" />

      {/* Search */}
      <div className="relative">
        <Search className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground" />
        <Input
          type="search"
          placeholder="Search sources…"
          className="pl-12 h-11"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
      </div>

      {/* Followed Sources */}
      <div>
        <h2 className="text-lg font-semibold mb-4">Following ({followedSources.length})</h2>
        <div className="grid gap-4">
          {sources
            .filter((s) => followedSources.includes(s.name))
            .map((source) => (
              <Card key={source.name}>
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <h3 className="font-semibold text-lg text-foreground">{source.name}</h3>
                      <div className="flex gap-2 mt-2">
                        <Badge variant="outline">{source.category}</Badge>
                        <Badge variant="secondary">{source.followers}</Badge>
                      </div>
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => toggleSource(source.name)}
                      className="text-destructive hover:text-destructive"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
        </div>
      </div>

      {/* Available Sources */}
      <div>
        <h2 className="text-lg font-semibold mb-4">Available Sources</h2>
        <div className="grid gap-4">
          {filteredSources
            .filter((s) => !followedSources.includes(s.name))
            .map((source) => (
              <Card key={source.name} className="hover:border-primary/50 transition-colors">
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <h3 className="font-semibold text-lg text-foreground">{source.name}</h3>
                      <div className="flex gap-2 mt-2">
                        <Badge variant="outline">{source.category}</Badge>
                        <Badge variant="secondary">{source.followers}</Badge>
                        <Badge className="bg-green-500/10 text-green-600 border-green-500/20">
                          {source.reliability}
                        </Badge>
                      </div>
                    </div>
                    <Button variant="outline" size="sm" onClick={() => toggleSource(source.name)} className="gap-2">
                      <Star className="h-4 w-4" />
                      Follow
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
        </div>
      </div>
    </div>
  )
}
