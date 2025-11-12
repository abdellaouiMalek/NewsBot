"use client"

import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { useGenerateResponse } from "@/lib/api"
import { Article } from "@/lib/api/schemas/article.schema"
import { cn } from "@/lib/utils"
import { Clock, Filter, Send, Sparkles, Tag, X } from "lucide-react"
import { useEffect, useRef, useState } from "react"

interface Message {
  id: string
  type: "user" | "agent"
  content: string
  timestamp: Date
  action?: {
    type: "filter" | "sort" | "search" | "category"
    value: string
  }
}

interface ChatAgentPanelProps {
  onClose?: () => void
  onArticlesUpdate?: (articles: Article[]) => void
}

const suggestedActions = [
  { icon: Filter, label: "Tech News", action: "What are the latest developments in AI technology?" },
  { icon: Clock, label: "Recent Events", action: "What happened in the news today?" },
  { icon: Tag, label: "Trending", action: "What are the trending topics right now?" },
  { icon: Sparkles, label: "Summary", action: "Summarize the top news stories" },
]

export function ChatAgentPanel({ onClose, onArticlesUpdate }: ChatAgentPanelProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      type: "agent",
      content:
        "Hi! I'm your NewsBot AI assistant. Ask me questions about news articles, and I'll search our database and provide factual, context-aware answers with sources.",
      timestamp: new Date(),
    },
  ])
  const [input, setInput] = useState("")
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Use the new API hook
  const generateMutation = useGenerateResponse()

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSendMessage = async (text: string) => {
    if (!text.trim()) return

    const userMessage: Message = {
      id: Date.now().toString(),
      type: "user",
      content: text,
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, userMessage])
    setInput("")

    try {
      // Use the mutation to call the API
      const response = await generateMutation.mutateAsync({
        query: text,
        k: 5,
      })

      // Extract the answer, sources, and articles from the RAG pipeline response
      const agentResponse = response.answer || "I couldn't generate a response. Please try again."
      const sources = response.sources || []
      const articles = response.articles || []
      
      // Count sources
      const sourceCount = sources.length

      const agentMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: "agent",
        content: agentResponse,
        timestamp: new Date(),
        action: sourceCount > 0 ? { type: "search", value: `${sourceCount} sources` } : undefined,
      }

      setMessages((prev) => [...prev, agentMessage])

      // Update parent component with the articles used in the response
      if (onArticlesUpdate && articles.length > 0) {
        onArticlesUpdate(articles)
      }
    } catch (error) {
      console.error("Error calling /generate API:", error)
      
      // Show error message to user
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: "agent",
        content: `Sorry, I encountered an error: ${error instanceof Error ? error.message : "Unknown error"}. Please make sure the API server is running.`,
        timestamp: new Date(),
      }

      setMessages((prev) => [...prev, errorMessage])
    }
  }

  return (
    <aside className="hidden md:flex w-140 min-w-80 border-l border-border bg-card p-6 flex-col overflow-hidden relative">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold flex items-center gap-2 text-foreground">
            <Sparkles className="h-5 w-5 text-primary" />
            NewsBot Assistant
          </h2>
          <p className="text-xs text-muted-foreground mt-1">Ask questions about news and get AI-powered answers</p>
        </div>
        <Button variant="ghost" size="icon" onClick={onClose} className="h-8 w-8 shrink-0" title="Close chat assistant">
          <X className="h-4 w-4" />
          <span className="sr-only">Close chat assistant</span>
        </Button>
      </div>

      <div className="flex-1 overflow-y-auto mb-4 space-y-4 pr-2">
        {messages.map((message) => (
          <div key={message.id} className={cn("flex", message.type === "user" ? "justify-end" : "justify-start")}>
            <div
              className={cn(
                "max-w-xl w-[85%] px-4 py-3 rounded-lg text-sm leading-relaxed",
                message.type === "user"
                  ? "bg-primary text-primary-foreground rounded-br-none"
                  : "bg-muted text-foreground rounded-bl-none border border-border",
              )}
            >
              <p className="whitespace-pre-wrap text-balance">{message.content}</p>
              {message.action && (
                <Badge variant="secondary" className="mt-2 text-xs">
                  {message.action.type}: {message.action.value}
                </Badge>
              )}
              <p className="text-xs opacity-70 mt-2">
                {message.timestamp.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
              </p>
            </div>
          </div>
        ))}
        {generateMutation.isPending && (
          <div className="flex justify-start">
            <div className="bg-muted text-foreground px-4 py-3 rounded-lg rounded-bl-none border border-border">
              <div className="flex flex-col gap-2">
                <div className="flex gap-2">
                  <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce" />
                  <div
                    className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce"
                    style={{ animationDelay: "0.2s" }}
                  />
                  <div
                    className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce"
                    style={{ animationDelay: "0.4s" }}
                  />
                </div>
                <p className="text-xs text-muted-foreground">
                  Searching articles and generating response...
                </p>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {messages.length <= 1 && (
        <div className="mb-4 space-y-2">
          <p className="text-xs text-muted-foreground font-medium">Quick actions:</p>
          <div className="grid grid-cols-2 gap-2">
            {suggestedActions.map((action) => {
              const Icon = action.icon
              return (
                <Button
                  key={action.label}
                  variant="outline"
                  size="sm"
                  className="text-xs h-auto py-2 flex flex-col items-center gap-1 bg-transparent"
                  onClick={() => handleSendMessage(action.action)}
                >
                  <Icon className="h-4 w-4" />
                  <span className="text-center">{action.label}</span>
                </Button>
              )
            })}
          </div>
        </div>
      )}

      <div className="flex gap-2">
        <Input
          placeholder="Ask me anything..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault()
              handleSendMessage(input)
            }
          }}
          disabled={generateMutation.isPending}
          className="text-sm"
        />
        <Button
          size="icon"
          onClick={() => handleSendMessage(input)}
          disabled={generateMutation.isPending || !input.trim()}
          className="shrink-0"
        >
          <Send className="h-4 w-4" />
          <span className="sr-only">Send message</span>
        </Button>
      </div>
    </aside>
  )
}
