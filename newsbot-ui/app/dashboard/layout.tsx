"use client"

import type React from "react"

import { ChatAgentPanel } from "@/components/chat-agent-panel"
import { ChatModal } from "@/components/chat-modal"
import { PreferencesModal } from "@/components/preferences-modal"
import { ProtectedRoute } from "@/components/protected-route"
import { Sidebar } from "@/components/sidebar"
import { Button } from "@/components/ui/button"
import { Article } from "@/lib/api/schemas/article.schema"
import { Menu, MessageSquare, X } from "lucide-react"
import { createContext, useContext, useState } from "react"

// Context for LLM-controlled articles
interface DashboardContextType {
  llmArticles: Article[] | null
  setLlmArticles: (articles: Article[] | null) => void
}

const DashboardContext = createContext<DashboardContextType | undefined>(undefined)

export function useDashboard() {
  const context = useContext(DashboardContext)
  if (!context) {
    throw new Error("useDashboard must be used within DashboardLayout")
  }
  return context
}

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const [isChatOpen, setIsChatOpen] = useState(false)
  const [isPreferencesOpen, setIsPreferencesOpen] = useState(false)
  const [isSidebarOpen, setIsSidebarOpen] = useState(false)
  const [isChatPanelOpen, setIsChatPanelOpen] = useState(false)
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false)
  const [llmArticles, setLlmArticles] = useState<Article[] | null>(null)

  return (
    <ProtectedRoute>
      <DashboardContext.Provider value={{ llmArticles, setLlmArticles }}>
        <div className="flex h-screen overflow-hidden bg-background">
          <div className={`${isSidebarOpen ? "block" : "hidden"} md:block fixed md:relative z-40 h-full`}>
            <Sidebar
              onOpenPreferences={() => setIsPreferencesOpen(true)}
              isCollapsed={isSidebarCollapsed}
              onToggleCollapse={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
            />
          </div>

          {isSidebarOpen && (
            <div className="fixed inset-0 bg-black/50 md:hidden z-30" onClick={() => setIsSidebarOpen(false)} />
          )}

          <main className="flex-1 overflow-y-auto scrollbar-hide flex flex-col w-full">
            <div className="md:hidden flex items-center gap-4 p-4 border-b border-border bg-background sticky top-0 z-20">
              <Button variant="ghost" size="icon" onClick={() => setIsSidebarOpen(!isSidebarOpen)} className="h-10 w-10">
                {isSidebarOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
                <span className="sr-only">Toggle sidebar</span>
              </Button>
              <h2 className="text-lg font-semibold text-foreground">NewsBot AI</h2>
            </div>

            <div className="w-full max-w-4xl mx-auto px-4 md:px-6 py-4 md:py-6 flex-1">{children}</div>
          </main>

          {isChatPanelOpen && (
            <ChatAgentPanel
              onClose={() => setIsChatPanelOpen(false)}
              onArticlesUpdate={(articles) => setLlmArticles(articles)}
            />
          )}

          {!isChatPanelOpen && (<Button
            size="lg"
            className="fixed bottom-6 right-6 h-14 w-14 rounded-full shadow-lg hover:shadow-xl transition-all z-50"
            onClick={() => {
              if (window.innerWidth < 768) {
                setIsChatOpen(true)
              } else {
                setIsChatPanelOpen(true)
              }
            }}
          >
            <MessageSquare className="h-6 w-6" />
            <span className="sr-only">Chat with NewsBot</span>
          </Button>)}

          <ChatModal open={isChatOpen} onOpenChange={setIsChatOpen} />
          <PreferencesModal open={isPreferencesOpen} onOpenChange={setIsPreferencesOpen} />
        </div>
      </DashboardContext.Provider>
    </ProtectedRoute>
  )
}
