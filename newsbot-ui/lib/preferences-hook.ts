"use client"

import { useState, useEffect, useCallback } from "react"
import { createBrowserClient } from "@supabase/ssr"

export interface ArticleFeedback {
  articleId: number
  headline: string
  category: string
  rating: "like" | "dislike" | "neutral"
  relevant: boolean
  timestamp: number
}

export interface UserPreferences {
  favoriteCategories: Record<string, number>
  likedArticles: number[]
  dislikedArticles: number[]
  feedbackHistory: ArticleFeedback[]
}

const supabase = createBrowserClient(process.env.NEXT_PUBLIC_SUPABASE_URL!, process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!)

export function usePreferences() {
  const [preferences, setPreferences] = useState<UserPreferences>({
    favoriteCategories: {},
    likedArticles: [],
    dislikedArticles: [],
    feedbackHistory: [],
  })
  const [loading, setLoading] = useState(true)
  const [userId, setUserId] = useState<string | null>(null)

  // Load user and preferences from Supabase
  useEffect(() => {
    const loadPreferences = async () => {
      try {
        const {
          data: { user },
        } = await supabase.auth.getUser()
        setUserId(user?.id || null)

        if (user) {
          const { data, error } = await supabase.from("user_preferences").select("*").eq("user_id", user.id).single()

          if (error && error.code !== "PGRST116") {
            console.error("Error loading preferences:", error)
          } else if (data) {
            setPreferences({
              favoriteCategories: data.preferred_categories || {},
              likedArticles: [],
              dislikedArticles: [],
              feedbackHistory: [],
            })
          }
        }
      } catch (error) {
        console.error("Failed to load preferences:", error)
      } finally {
        setLoading(false)
      }
    }

    loadPreferences()
  }, [])

  // Add feedback for an article
  const addFeedback = useCallback(
    async (
      articleId: number,
      headline: string,
      category: string,
      rating: "like" | "dislike" | "neutral",
      relevant: boolean,
    ) => {
      if (!userId) return

      try {
        const { error: feedbackError } = await supabase.from("article_feedback").insert({
          user_id: userId,
          article_id: articleId.toString(),
          liked: rating === "like",
          relevant,
          category,
          source: "newsbot",
        })

        if (feedbackError) console.error("Error saving feedback:", feedbackError)

        // Update local preferences
        const newPreferences = { ...preferences }

        if (!newPreferences.favoriteCategories[category]) {
          newPreferences.favoriteCategories[category] = 0
        }

        if (rating === "like") {
          newPreferences.favoriteCategories[category] += 2
          if (!newPreferences.likedArticles.includes(articleId)) {
            newPreferences.likedArticles.push(articleId)
          }
        } else if (rating === "dislike") {
          newPreferences.favoriteCategories[category] -= 1
          if (!newPreferences.dislikedArticles.includes(articleId)) {
            newPreferences.dislikedArticles.push(articleId)
          }
        }

        if (relevant) {
          newPreferences.favoriteCategories[category] += 1
        }

        newPreferences.feedbackHistory.push({
          articleId,
          headline,
          category,
          rating,
          relevant,
          timestamp: Date.now(),
        })

        const { error: prefError } = await supabase
          .from("user_preferences")
          .upsert({
            user_id: userId,
            preferred_categories: newPreferences.favoriteCategories,
            tone: "balanced",
          })
          .eq("user_id", userId)

        if (prefError) console.error("Error updating preferences:", prefError)

        setPreferences(newPreferences)
      } catch (error) {
        console.error("Failed to add feedback:", error)
      }
    },
    [userId, preferences],
  )

  // Get personalization score for an article
  const getPersonalizationScore = (category: string, articleId: number): number => {
    let score = 0
    score += (preferences.favoriteCategories[category] || 0) * 10
    if (preferences.likedArticles.includes(articleId)) score += 50
    if (preferences.dislikedArticles.includes(articleId)) score -= 50
    return score
  }

  // Get sorted articles based on preferences
  const sortArticlesByPreference = (articles: any[]) => {
    return [...articles].sort((a, b) => {
      const scoreA = getPersonalizationScore(a.category, a.id)
      const scoreB = getPersonalizationScore(b.category, b.id)
      return scoreB - scoreA
    })
  }

  return {
    preferences,
    addFeedback,
    getPersonalizationScore,
    sortArticlesByPreference,
    loading,
  }
}
