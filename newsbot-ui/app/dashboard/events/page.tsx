"use client"

import { useState } from "react"
import { PageHeader } from "@/components/page-header"
import { EventTimeline } from "@/components/event-timeline"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Search } from "lucide-react"

const featuredEvents = [
  {
    id: 1,
    title: "Palestine-Israel Conflict",
    description: "Ongoing geopolitical tensions and military operations",
    category: "Politics",
  },
  {
    id: 2,
    title: "Climate Crisis 2024",
    description: "Global warming and environmental challenges",
    category: "Science",
  },
  {
    id: 3,
    title: "AI Revolution",
    description: "Rapid advancement in artificial intelligence",
    category: "Tech",
  },
  {
    id: 4,
    title: "Global Economic Shifts",
    description: "Market trends and economic developments",
    category: "Business",
  },
]

export default function EventsPage() {
  const [selectedEvent, setSelectedEvent] = useState<(typeof featuredEvents)[0] | null>(null)
  const [searchQuery, setSearchQuery] = useState("")

  const filteredEvents = featuredEvents.filter(
    (event) =>
      event.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      event.description.toLowerCase().includes(searchQuery.toLowerCase()),
  )

  return (
    <div className="flex flex-col gap-6">
      <PageHeader title="Events" description="Explore timelines of major events and their evolution" />

      {/* Search Section */}
      <div className="flex gap-2">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search events..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10"
          />
        </div>
      </div>

      {/* Events Grid */}
      {!selectedEvent ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {filteredEvents.map((event) => (
            <button
              key={event.id}
              onClick={() => setSelectedEvent(event)}
              className="p-4 rounded-lg border border-border bg-card hover:bg-accent transition-colors text-left"
            >
              <div className="flex items-start justify-between gap-3">
                <div className="flex-1">
                  <h3 className="font-semibold text-foreground">{event.title}</h3>
                  <p className="text-sm text-muted-foreground mt-1">{event.description}</p>
                </div>
                <span className="text-xs px-2 py-1 rounded-full bg-primary/10 text-primary whitespace-nowrap">
                  {event.category}
                </span>
              </div>
            </button>
          ))}
        </div>
      ) : (
        <div className="space-y-4">
          <Button variant="outline" onClick={() => setSelectedEvent(null)}>
            ← Back to Events
          </Button>
          <EventTimeline event={selectedEvent} />
        </div>
      )}
    </div>
  )
}
