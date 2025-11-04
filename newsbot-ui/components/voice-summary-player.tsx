"use client"

import { useState, useEffect } from "react"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Play, Pause, Volume2, Download, X } from "lucide-react"
import { TextToSpeechManager, generateTrendsSummary } from "@/lib/text-to-speech"

interface VoiceSummaryPlayerProps {
  trends: Array<{ tag: string; growth: string; posts: string }>
  onClose?: () => void
}

export function VoiceSummaryPlayer({ trends, onClose }: VoiceSummaryPlayerProps) {
  const [isPlaying, setIsPlaying] = useState(false)
  const [speed, setSpeed] = useState(1)
  const [ttsManager] = useState(() => new TextToSpeechManager())
  const [progress, setProgress] = useState(0)

  const summaryText = generateTrendsSummary(trends)

  useEffect(() => {
    return () => {
      ttsManager.stop()
    }
  }, [ttsManager])

  const handlePlayPause = () => {
    if (isPlaying) {
      ttsManager.pause()
      setIsPlaying(false)
    } else {
      ttsManager.speak(summaryText, { rate: speed }, () => {
        setIsPlaying(false)
        setProgress(0)
      })
      setIsPlaying(true)
    }
  }

  const handleSpeedChange = (newSpeed: number) => {
    setSpeed(newSpeed)
    if (isPlaying) {
      ttsManager.stop()
      ttsManager.speak(summaryText, { rate: newSpeed }, () => {
        setIsPlaying(false)
        setProgress(0)
      })
    }
  }

  const handleDownload = async () => {
    try {
      // Create a simple audio blob using Web Audio API
      const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)()
      const oscillator = audioContext.createOscillator()
      const gainNode = audioContext.createGain()

      oscillator.connect(gainNode)
      gainNode.connect(audioContext.destination)

      // Generate a simple tone pattern as placeholder
      oscillator.frequency.value = 440
      gainNode.gain.setValueAtTime(0.1, audioContext.currentTime)
      gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5)

      oscillator.start(audioContext.currentTime)
      oscillator.stop(audioContext.currentTime + 0.5)

      // Create download link
      const link = document.createElement("a")
      link.href = "#"
      link.download = "trends-summary.wav"
      link.click()
    } catch (error) {
      console.error("Download failed:", error)
    }
  }

  return (
    <Card className="bg-gradient-to-br from-primary/5 to-accent/5 border-primary/20">
      <CardContent className="pt-6">
        <div className="space-y-4">
          {/* Header */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Volume2 className="h-5 w-5 text-primary" />
              <h3 className="font-semibold text-foreground">Trends Voice Summary</h3>
            </div>
            {onClose && (
              <button onClick={onClose} className="text-muted-foreground hover:text-foreground transition-colors">
                <X className="h-4 w-4" />
              </button>
            )}
          </div>

          {/* Summary Text Preview */}
          <p className="text-sm text-muted-foreground line-clamp-2">{summaryText}</p>

          {/* Progress Bar */}
          <div className="w-full bg-muted rounded-full h-1">
            <div
              className="bg-primary h-1 rounded-full transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>

          {/* Controls */}
          <div className="flex items-center justify-between gap-3">
            <Button onClick={handlePlayPause} size="sm" className="gap-2" variant={isPlaying ? "default" : "outline"}>
              {isPlaying ? (
                <>
                  <Pause className="h-4 w-4" />
                  Pause
                </>
              ) : (
                <>
                  <Play className="h-4 w-4" />
                  Play
                </>
              )}
            </Button>

            {/* Speed Control */}
            <div className="flex items-center gap-2">
              <span className="text-xs text-muted-foreground">Speed:</span>
              <select
                value={speed}
                onChange={(e) => handleSpeedChange(Number.parseFloat(e.target.value))}
                className="text-xs bg-background border border-border rounded px-2 py-1 text-foreground"
              >
                <option value={0.75}>0.75x</option>
                <option value={1}>1x</option>
                <option value={1.25}>1.25x</option>
                <option value={1.5}>1.5x</option>
                <option value={2}>2x</option>
              </select>
            </div>

            {/* Download Button */}
            <Button onClick={handleDownload} size="sm" variant="outline" className="gap-2 bg-transparent">
              <Download className="h-4 w-4" />
              <span className="hidden sm:inline">Download</span>
            </Button>
          </div>

          {/* Status */}
          <p className="text-xs text-muted-foreground text-center">
            {isPlaying ? "Playing audio summary..." : "Ready to play"}
          </p>
        </div>
      </CardContent>
    </Card>
  )
}
