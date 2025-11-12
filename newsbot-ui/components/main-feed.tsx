"use client"

import { NewsCard } from "@/components/news-card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { cn } from "@/lib/utils"
import { Search, Sparkles, X } from "lucide-react"
import { useEffect, useState } from "react"

import { useDashboard } from "@/app/dashboard/layout"
import { useCategories, useInfiniteArticles } from '@/lib/api'

export function MainFeed() {
  const [activeCategory, setActiveCategory] = useState('All')
  const { data: categories, isLoading: isCategoriesLoading } = useCategories();
  const { llmArticles, setLlmArticles } = useDashboard()

  // When remote categories load, pick the first available if current active isn't present
  useEffect(() => {
    if (categories && categories.length) {
      if (!categories.includes(activeCategory)) {
        setActiveCategory(categories[0]);
      }
    }
  }, [categories]);

  // Articles - fetched via useInfiniteArticles
  // If activeCategory is 'All' or falsy, fetch all articles (no category filter)
  const articlesParams = !activeCategory || activeCategory === 'All'
    ? { page_size: 10 }
    : { page_size: 10, category: activeCategory };
  const {
    data: articlePages,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
    isLoading: isArticlesLoading,
    isError: isArticlesError,
  } = useInfiniteArticles(articlesParams);

  const regularArticles = articlePages?.pages.flatMap((p) => p.articles) ?? [];
  
  // Use LLM articles if available, otherwise use regular articles
  const articles = llmArticles ?? regularArticles
  const isLlmMode = llmArticles !== null

  const [searchQuery, setSearchQuery] = useState("")

  return (
    <div className="w-full space-y-4 md:space-y-6">
      {/* LLM Mode Banner */}
      {isLlmMode && (
        <div className="bg-primary/10 border border-primary/20 rounded-lg p-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-primary" />
            <div>
              <p className="text-sm font-medium text-foreground">AI-Curated Results</p>
              <p className="text-xs text-muted-foreground">
                Showing {articles.length} article{articles.length !== 1 ? 's' : ''} selected by the AI assistant
              </p>
            </div>
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setLlmArticles(null)}
            className="gap-2"
          >
            <X className="h-4 w-4" />
            Clear
          </Button>
        </div>
      )}

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

      {/* Category Tabs - Hide in LLM mode */}
      {!isLlmMode && (
        <div className="flex gap-2 overflow-x-auto pb-2 -mx-4 md:mx-0 px-4 md:px-0 flex-nowrap snap-x snap-mandatory">
          {(categories ?? ['All']).map((category) => (
            <Button
              key={category}
              variant={activeCategory === category ? "default" : "outline"}
              className={cn(
                "flex-none snap-start whitespace-nowrap text-sm md:text-base",
                activeCategory === category && "bg-primary text-primary-foreground",
              )}
              onClick={() => setActiveCategory(category)}
            >
              {category}
            </Button>
          ))}
        </div>
      )}

      {/* News Feed */}
      <div className="space-y-3 md:space-y-4">
        {!isLlmMode && isArticlesLoading ? (
          <div className="text-sm text-muted-foreground">Loading articles…</div>
        ) : !isLlmMode && isArticlesError ? (
          <div className="text-sm text-destructive">Failed to load articles.</div>
        ) : articles.length === 0 ? (
          <div className="text-sm text-muted-foreground">No articles yet.</div>
        ) : (
          articles.map((item, idx) => (
            <NewsCard
              key={item.id}
              id={idx + 1}
              articleId={item.article_id}
              headline={item.title}
              summary={item.summary ?? (item.content ? item.content.slice(0, 200) : '')}
              source={item.source_name}
              time={item.published_at ? new Date(String(item.published_at)).toLocaleString() : ''}
              category={item.category ?? ''}
            />
          ))
        )}

        {!isLlmMode && hasNextPage && (
          <div className="flex justify-center pt-4">
            <Button onClick={() => fetchNextPage()} disabled={isFetchingNextPage}>
              {isFetchingNextPage ? 'Loading...' : 'Load more'}
            </Button>
          </div>
        )}
      </div>
    </div>
  )
}
