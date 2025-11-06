"use client"

import { useState } from "react"
import { Sidebar } from "@/components/sidebar"
import { MainFeed } from "@/components/main-feed"
import { RightSidebar } from "@/components/right-sidebar"
import { ChatModal } from "@/components/chat-modal"
import { PreferencesModal } from "@/components/preferences-modal"
import { Button } from "@/components/ui/button"
import { MessageSquare } from "lucide-react"

export function DashboardLayout() {
  const [isChatOpen, setIsChatOpen] = useState(false)
  const [isPreferencesOpen, setIsPreferencesOpen] = useState(false)

  return (
    <div className="flex h-screen overflow-hidden bg-background">
      <Sidebar onOpenPreferences={() => setIsPreferencesOpen(true)} />

      <main className="flex-1 overflow-y-auto">
        <MainFeed />
      </main>

      <RightSidebar />

      {/* Floating Chat Button */}
      <Button
        size="lg"
        className="fixed bottom-6 right-6 h-14 w-14 rounded-full shadow-lg hover:shadow-xl transition-all"
        onClick={() => setIsChatOpen(true)}
      >
        <MessageSquare className="h-6 w-6" />
        <span className="sr-only">Chat with NewsBot</span>
      </Button>

      <ChatModal open={isChatOpen} onOpenChange={setIsChatOpen} />
      <PreferencesModal open={isPreferencesOpen} onOpenChange={setIsPreferencesOpen} />
    </div>
  )
}
