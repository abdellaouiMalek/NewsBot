"use client"

import { useState, useRef, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Send, Sparkles, Filter, Clock, Tag, ChevronRight } from "lucide-react"
import { cn } from "@/lib/utils"

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

interface ChatAgentProps {
  onToggle?: () => void
}

const suggestedActions = [
  { icon: Filter, label: "Filter by Tech", action: "Show me only tech news" },
  { icon: Clock, label: "Last 24h", action: "Filter news from the last 24 hours" },
  { icon: Tag, label: "Trending", action: "Show trending topics" },
  { icon: Sparkles, label: "AI Summary", action: "Summarize today's top stories" },
]

export function ChatAgent({ onToggle }: ChatAgentProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      type: "agent",
      content:
        "Hi! I'm your NewsBot AI assistant. I can help you filter, search, and organize your news feed. What would you like to do?",
      timestamp: new Date(),
    },
  ])
  const [input, setInput] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSendMessage = async (text: string) => {
    if (!text.trim()) return

    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      type: "user",
      content: text,
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, userMessage])
    setInput("")
    setIsLoading(true)

    // Simulate agent response with action detection
    setTimeout(() => {
      let agentResponse = ""
      let action: Message["action"] | undefined

      const lowerText = text.toLowerCase()

      if (lowerText.includes("tech") || lowerText.includes("technology")) {
        agentResponse = "Filtering news to show only Technology articles. I found 24 relevant stories for you."
        action = { type: "filter", value: "tech" }
      } else if (lowerText.includes("last 24") || lowerText.includes("today")) {
        agentResponse = "Showing news from the last 24 hours. Found 156 articles matching your criteria."
        action = { type: "filter", value: "24h" }
      } else if (lowerText.includes("trending") || lowerText.includes("popular")) {
        agentResponse =
          "Here are today's trending topics: #AI (12.5K posts), #Elections (15.3K posts), #Climate (8.2K posts)"
        action = { type: "sort", value: "trending" }
      } else if (lowerText.includes("summary") || lowerText.includes("summarize")) {
        agentResponse =
          "📰 Top Stories Summary:\n1. Major tech acquisition announced\n2. Markets respond to Fed decision\n3. International summit begins\n\nWould you like more details on any of these?"
        action = { type: "sort", value: "summary" }
      } else if (lowerText.includes("business") || lowerText.includes("finance")) {
        agentResponse =
          "Filtering to Business & Finance news. Found 42 articles. Top story: Markets respond to Federal Reserve decision."
        action = { type: "filter", value: "business" }
      } else if (lowerText.includes("search") || lowerText.includes("find")) {
        agentResponse = "I can help you search! What topic or keyword would you like me to search for?"
        action = { type: "search", value: text }
      } else {
        agentResponse =
          "I can help you with that! Try asking me to filter by category (Tech, Business, Science), sort by trending, or summarize today's news."
      }

      const agentMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: "agent",
        content: agentResponse,
        timestamp: new Date(),
        action,
      }

      setMessages((prev) => [...prev, agentMessage])
      setIsLoading(false)
    }, 600)
  }

  return (
    <aside className="w-80 border-l border-border bg-card p-6 flex flex-col overflow-hidden relative">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold flex items-center gap-2 text-foreground">
            <Sparkles className="h-5 w-5 text-primary" />
            NewsBot Assistant
          </h2>
          <p className="text-xs text-muted-foreground mt-1">Ask me to filter, search, or organize your feed</p>
        </div>
        <Button
          variant="ghost"
          size="icon"
          onClick={onToggle}
          className="h-8 w-8 shrink-0"
          title="Collapse chat assistant"
        >
          <ChevronRight className="h-4 w-4" />
          <span className="sr-only">Collapse chat assistant</span>
        </Button>
      </div>

      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto mb-4 space-y-4 pr-2">
        {messages.map((message) => (
          <div key={message.id} className={cn("flex", message.type === "user" ? "justify-end" : "justify-start")}>
            <div
              className={cn(
                "max-w-xs px-4 py-3 rounded-lg text-sm leading-relaxed",
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
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-muted text-foreground px-4 py-3 rounded-lg rounded-bl-none border border-border">
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
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Suggested Actions */}
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

      {/* Input Area */}
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
          disabled={isLoading}
          className="text-sm"
        />
        <Button
          size="icon"
          onClick={() => handleSendMessage(input)}
          disabled={isLoading || !input.trim()}
          className="shrink-0"
        >
          <Send className="h-4 w-4" />
          <span className="sr-only">Send message</span>
        </Button>
      </div>
    </aside>
  )
}
