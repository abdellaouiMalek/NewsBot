"use client"

import { useState } from "react"
import { PageHeader } from "@/components/page-header"
import { NewsCard } from "@/components/news-card"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Sparkles, Plus } from "lucide-react"

const categories = [
  { name: "Artificial Intelligence", icon: "🤖", articles: 342 },
  { name: "Climate & Environment", icon: "🌍", articles: 287 },
  { name: "Space & Astronomy", icon: "🚀", articles: 156 },
  { name: "Biotechnology", icon: "🧬", articles: 198 },
  { name: "Renewable Energy", icon: "⚡", articles: 224 },
  { name: "Quantum Computing", icon: "💻", articles: 89 },
]

const discoverNews = [
  {
    id: 1,
    headline: "Breakthrough in Fusion Energy Technology",
    summary:
      "Scientists achieve record-breaking results in controlled nuclear fusion, bringing clean energy closer to reality.",
    source: "Science Daily",
    time: "1h ago",
    category: "Energy",
  },
  {
    id: 2,
    headline: "New Species Discovered in Amazon Rainforest",
    summary:
      "Researchers identify previously unknown species during biodiversity expedition, highlighting the importance of conservation.",
    source: "National Geographic",
    time: "3h ago",
    category: "Science",
  },
  {
    id: 3,
    headline: "Breakthrough in Alzheimer's Research",
    summary:
      "New treatment shows promise in slowing cognitive decline, offering hope to millions of patients worldwide.",
    source: "Medical News Today",
    time: "5h ago",
    category: "Health",
  },
]

export default function DiscoverPage() {
  const [followedCategories, setFollowedCategories] = useState<string[]>([])

  const toggleCategory = (categoryName: string) => {
    setFollowedCategories((prev) =>
      prev.includes(categoryName) ? prev.filter((c) => c !== categoryName) : [...prev, categoryName],
    )
  }

  return (
    <div className="space-y-6">
      <PageHeader title="Discover" description="Explore new topics and expand your news horizons" />

      {/* Category Grid */}
      <div>
        <h2 className="text-lg font-semibold mb-4">Explore Categories</h2>
        <div className="grid grid-cols-2 gap-4">
          {categories.map((category) => (
            <Card
              key={category.name}
              className="hover:border-primary/50 transition-colors cursor-pointer"
              onClick={() => toggleCategory(category.name)}
            >
              <CardContent className="pt-6">
                <div className="flex items-start justify-between">
                  <div>
                    <p className="text-2xl mb-2">{category.icon}</p>
                    <h3 className="font-semibold text-foreground">{category.name}</h3>
                    <p className="text-sm text-muted-foreground mt-1">{category.articles} articles</p>
                  </div>
                  <Button
                    size="sm"
                    variant={followedCategories.includes(category.name) ? "default" : "outline"}
                    className="gap-1"
                  >
                    <Plus className="h-4 w-4" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>

      {/* Trending Discoveries */}
      <div>
        <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Sparkles className="h-5 w-5 text-primary" />
          Trending Discoveries
        </h2>
        <div className="space-y-4">
          {discoverNews.map((item) => (
            <NewsCard key={item.id} {...item} />
          ))}
        </div>
      </div>
    </div>
  )
}
