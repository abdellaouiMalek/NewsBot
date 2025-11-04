"use client"

import { useState } from "react"
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"
import { Checkbox } from "@/components/ui/checkbox"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Separator } from "@/components/ui/separator"

interface PreferencesModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
}

const topics = ["Politics", "Technology", "Business", "Science", "Health", "Sports", "Entertainment", "Environment"]

const sources = ["Reuters", "Associated Press", "Bloomberg", "TechCrunch", "The Guardian", "BBC News", "CNN", "NPR"]

export function PreferencesModal({ open, onOpenChange }: PreferencesModalProps) {
  const [selectedTopics, setSelectedTopics] = useState<string[]>(["Technology", "Science"])
  const [selectedSources, setSelectedSources] = useState<string[]>(["Reuters", "TechCrunch"])
  const [tone, setTone] = useState("objective")

  const toggleTopic = (topic: string) => {
    setSelectedTopics((prev) => (prev.includes(topic) ? prev.filter((t) => t !== topic) : [...prev, topic]))
  }

  const toggleSource = (source: string) => {
    setSelectedSources((prev) => (prev.includes(source) ? prev.filter((s) => s !== source) : [...prev, source]))
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[80vh] flex flex-col p-0">
        <DialogHeader className="p-6 pb-4 border-b">
          <DialogTitle className="text-xl">Personalization Settings</DialogTitle>
          <DialogDescription>Customize your news feed preferences and reading experience</DialogDescription>
        </DialogHeader>

        <ScrollArea className="flex-1 p-6">
          <div className="space-y-6">
            {/* Topics */}
            <div className="space-y-4">
              <div>
                <h3 className="text-lg font-semibold mb-1">Preferred Topics</h3>
                <p className="text-sm text-muted-foreground">Select topics you want to see in your feed</p>
              </div>
              <div className="grid grid-cols-2 gap-3">
                {topics.map((topic) => (
                  <div key={topic} className="flex items-center space-x-2">
                    <Checkbox
                      id={`topic-${topic}`}
                      checked={selectedTopics.includes(topic)}
                      onCheckedChange={() => toggleTopic(topic)}
                    />
                    <Label
                      htmlFor={`topic-${topic}`}
                      className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 cursor-pointer"
                    >
                      {topic}
                    </Label>
                  </div>
                ))}
              </div>
            </div>

            <Separator />

            {/* Sources */}
            <div className="space-y-4">
              <div>
                <h3 className="text-lg font-semibold mb-1">Trusted Sources</h3>
                <p className="text-sm text-muted-foreground">Choose your preferred news sources</p>
              </div>
              <div className="grid grid-cols-2 gap-3">
                {sources.map((source) => (
                  <div key={source} className="flex items-center space-x-2">
                    <Checkbox
                      id={`source-${source}`}
                      checked={selectedSources.includes(source)}
                      onCheckedChange={() => toggleSource(source)}
                    />
                    <Label
                      htmlFor={`source-${source}`}
                      className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 cursor-pointer"
                    >
                      {source}
                    </Label>
                  </div>
                ))}
              </div>
            </div>

            <Separator />

            {/* Tone */}
            <div className="space-y-4">
              <div>
                <h3 className="text-lg font-semibold mb-1">Content Tone</h3>
                <p className="text-sm text-muted-foreground">How would you like news to be presented?</p>
              </div>
              <RadioGroup value={tone} onValueChange={setTone}>
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="objective" id="objective" />
                  <Label htmlFor="objective" className="cursor-pointer">
                    <span className="font-medium">Objective</span>
                    <span className="text-sm text-muted-foreground block">Neutral, fact-based reporting</span>
                  </Label>
                </div>
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="analytical" id="analytical" />
                  <Label htmlFor="analytical" className="cursor-pointer">
                    <span className="font-medium">Analytical</span>
                    <span className="text-sm text-muted-foreground block">In-depth analysis and context</span>
                  </Label>
                </div>
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="casual" id="casual" />
                  <Label htmlFor="casual" className="cursor-pointer">
                    <span className="font-medium">Casual</span>
                    <span className="text-sm text-muted-foreground block">Easy-to-read, conversational style</span>
                  </Label>
                </div>
              </RadioGroup>
            </div>
          </div>
        </ScrollArea>

        <div className="p-6 pt-4 border-t flex justify-end gap-3">
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancel
          </Button>
          <Button onClick={() => onOpenChange(false)}>Save Preferences</Button>
        </div>
      </DialogContent>
    </Dialog>
  )
}
