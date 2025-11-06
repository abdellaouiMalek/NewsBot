"use client"

import { useState, useMemo } from "react"
import { PageHeader } from "@/components/page-header"
import { NewsCard } from "@/components/news-card"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Search, Filter, TrendingUp } from "lucide-react"
import { usePreferences } from "@/lib/preferences-hook"

const allArticles = [
  {
    id: 1,
    headline: "AI Breakthrough: New Model Achieves Human-Level Reasoning",
    summary:
      "Researchers announce a significant advancement in artificial intelligence, with a new model demonstrating unprecedented reasoning capabilities across multiple domains.",
    source: "TechCrunch",
    time: "2h ago",
    category: "Tech",
  },
  {
    id: 2,
    headline: "Quantum Computing Reaches New Milestone",
    summary:
      "Scientists successfully demonstrate quantum advantage in practical applications, marking a significant step toward commercial quantum computing.",
    source: "Nature",
    time: "4h ago",
    category: "Tech",
  },
  {
    id: 3,
    headline: "Tech Giants Announce Sustainability Initiatives",
    summary:
      "Major technology companies commit to carbon neutrality by 2030, pledging billions in green technology investments.",
    source: "Forbes",
    time: "6h ago",
    category: "Tech",
  },
  {
    id: 4,
    headline: "Global Climate Summit Reaches Historic Agreement",
    summary:
      "World leaders commit to ambitious carbon reduction targets in landmark climate accord, marking a turning point in international environmental policy.",
    source: "Reuters",
    time: "3h ago",
    category: "Politics",
  },
  {
    id: 5,
    headline: "Stock Markets Hit Record Highs",
    summary:
      "Major indices surge to all-time peaks as investors respond positively to strong earnings reports and favorable economic indicators.",
    source: "Bloomberg",
    time: "5h ago",
    category: "Business",
  },
]

export default function MyFeedPage() {
  const [searchQuery, setSearchQuery] = useState("")
  const { preferences, sortArticlesByPreference, getPersonalizationScore } = usePreferences()

  const personalizedArticles = useMemo(() => {
    const filtered = allArticles.filter(
      (item) =>
        item.headline.toLowerCase().includes(searchQuery.toLowerCase()) ||
        item.summary.toLowerCase().includes(searchQuery.toLowerCase()),
    )
    return sortArticlesByPreference(filtered)
  }, [searchQuery, preferences])

  const topCategories = Object.entries(preferences.favoriteCategories)
    .sort(([, a], [, b]) => b - a)
    .slice(0, 3)

  return (
    <div className="space-y-6">
      <PageHeader title="My Feed" description="Personalized news curated based on your interests and preferences" />

      {/* Search and Filter */}
      <div className="flex gap-3">
        <div className="flex-1 relative">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground" />
          <Input
            type="search"
            placeholder="Search your feed…"
            className="pl-12 h-11"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
        <Button variant="outline" className="gap-2 bg-transparent">
          <Filter className="h-4 w-4" />
          Filter
        </Button>
      </div>

      {/* Feed Stats */}
      <div className="grid grid-cols-3 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-3xl font-bold text-primary">{personalizedArticles.length}</p>
              <p className="text-sm text-muted-foreground mt-1">Articles</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-3xl font-bold text-primary">{Object.keys(preferences.favoriteCategories).length}</p>
              <p className="text-sm text-muted-foreground mt-1">Topics Followed</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-3xl font-bold text-primary">{preferences.likedArticles.length}</p>
              <p className="text-sm text-muted-foreground mt-1">Liked Articles</p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Top Categories */}
      {topCategories.length > 0 && (
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-2 mb-4">
              <TrendingUp className="h-5 w-5 text-primary" />
              <h3 className="font-semibold">Your Top Interests</h3>
            </div>
            <div className="flex flex-wrap gap-2">
              {topCategories.map(([category, score]) => (
                <div key={category} className="px-3 py-1 rounded-full bg-primary/10 text-primary text-sm font-medium">
                  {category} ({Math.round(score)})
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* News Feed */}
      <div className="space-y-4">
        {personalizedArticles.length > 0 ? (
          personalizedArticles.map((item) => <NewsCard key={item.id} {...item} />)
        ) : (
          <Card>
            <CardContent className="pt-6 text-center">
              <p className="text-muted-foreground">
                No articles found. Start giving feedback to personalize your feed!
              </p>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}
