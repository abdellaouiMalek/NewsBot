"use client"

import type React from "react"

import { useState } from "react"
import { Sidebar } from "@/components/sidebar"
import { ChatModal } from "@/components/chat-modal"
import { PreferencesModal } from "@/components/preferences-modal"
import { Button } from "@/components/ui/button"
import { MessageSquare, Menu, X } from "lucide-react"
import { ProtectedRoute } from "@/components/protected-route"
import { ChatAgentPanel } from "@/components/chat-agent-panel"

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const [isChatOpen, setIsChatOpen] = useState(false)
  const [isPreferencesOpen, setIsPreferencesOpen] = useState(false)
  const [isSidebarOpen, setIsSidebarOpen] = useState(false)
  const [isChatPanelOpen, setIsChatPanelOpen] = useState(false)
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false)

  return (
    <ProtectedRoute>
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

        {isChatPanelOpen && <ChatAgentPanel onClose={() => setIsChatPanelOpen(false)} />}

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
    </ProtectedRoute>
  )
}
