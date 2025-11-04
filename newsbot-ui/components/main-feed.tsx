"use client"

import { useState } from "react"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { NewsCard } from "@/components/news-card"
import { Search } from "lucide-react"
import { cn } from "@/lib/utils"

const categories = ["For You", "Breaking", "Politics", "Tech", "Business", "Science", "Sports", "Entertainment"]

const newsItems = [
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
    headline: "Global Climate Summit Reaches Historic Agreement",
    summary:
      "World leaders commit to ambitious carbon reduction targets in landmark climate accord, marking a turning point in international environmental policy.",
    source: "Reuters",
    time: "4h ago",
    category: "Politics",
  },
  {
    id: 3,
    headline: "Stock Markets Hit Record Highs Amid Economic Optimism",
    summary:
      "Major indices surge to all-time peaks as investors respond positively to strong earnings reports and favorable economic indicators.",
    source: "Bloomberg",
    time: "5h ago",
    category: "Business",
  },
  {
    id: 4,
    headline: "Scientists Discover Potential Cure for Rare Disease",
    summary:
      "Medical researchers identify promising treatment pathway that could revolutionize care for patients with previously untreatable genetic condition.",
    source: "Nature",
    time: "7h ago",
    category: "Science",
  },
  {
    id: 5,
    headline: "Championship Finals Draw Record Viewership Numbers",
    summary:
      "Historic sporting event captivates global audience, breaking previous records and highlighting the growing popularity of the sport worldwide.",
    source: "ESPN",
    time: "9h ago",
    category: "Sports",
  },
]

export function MainFeed() {
  const [activeCategory, setActiveCategory] = useState("For You")
  const [searchQuery, setSearchQuery] = useState("")

  return (
    <div className="w-full space-y-4 md:space-y-6">
      {/* Search Bar */}
      <div className="relative">
        <Search className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground" />
        <Input
          type="search"
          placeholder="Search news, topics, or keywords…"
          className="pl-12 h-12 text-base bg-card w-full"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
      </div>

      {/* Category Tabs */}
      <div className="flex gap-2 overflow-x-auto pb-2 scrollbar-hide -mx-4 md:mx-0 px-4 md:px-0">
        {categories.map((category) => (
          <Button
            key={category}
            variant={activeCategory === category ? "default" : "outline"}
            className={cn(
              "whitespace-nowrap text-sm md:text-base",
              activeCategory === category && "bg-primary text-primary-foreground",
            )}
            onClick={() => setActiveCategory(category)}
          >
            {category}
          </Button>
        ))}
      </div>

      {/* News Feed */}
      <div className="space-y-3 md:space-y-4">
        {newsItems.map((item) => (
          <NewsCard key={item.id} id={item.id} {...item} />
        ))}
      </div>
    </div>
  )
}
