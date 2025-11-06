export interface TextToSpeechOptions {
  rate?: number
  pitch?: number
  volume?: number
}

export class TextToSpeechManager {
  private utterance: SpeechSynthesisUtterance | null = null
  private isPlaying = false

  constructor() {
    if (typeof window !== "undefined" && !window.speechSynthesis) {
      console.warn("Speech Synthesis API not supported in this browser")
    }
  }

  speak(text: string, options: TextToSpeechOptions = {}, onEnd?: () => void) {
    if (!window.speechSynthesis) return

    // Cancel any ongoing speech
    window.speechSynthesis.cancel()

    this.utterance = new SpeechSynthesisUtterance(text)
    this.utterance.rate = options.rate || 1
    this.utterance.pitch = options.pitch || 1
    this.utterance.volume = options.volume || 1

    this.utterance.onend = () => {
      this.isPlaying = false
      onEnd?.()
    }

    this.utterance.onerror = () => {
      this.isPlaying = false
    }

    this.isPlaying = true
    window.speechSynthesis.speak(this.utterance)
  }

  pause() {
    if (window.speechSynthesis && this.isPlaying) {
      window.speechSynthesis.pause()
      this.isPlaying = false
    }
  }

  resume() {
    if (window.speechSynthesis && this.utterance) {
      window.speechSynthesis.resume()
      this.isPlaying = true
    }
  }

  stop() {
    if (window.speechSynthesis) {
      window.speechSynthesis.cancel()
      this.isPlaying = false
    }
  }

  getIsPlaying() {
    return this.isPlaying
  }
}

export function generateTrendsSummary(trends: Array<{ tag: string; growth: string; posts: string }>): string {
  const trendsList = trends.map((t) => `${t.tag} with ${t.growth} growth and ${t.posts} posts`).join(", ")
  return `Here are today's trending topics. ${trendsList}. These topics are gaining significant attention across the platform. Stay updated with the latest developments in these areas.`
}

export async function downloadAudio(text: string, filename = "summary.wav") {
  if (!window.speechSynthesis) return

  const utterance = new SpeechSynthesisUtterance(text)

  // Create a simple audio context for recording
  const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)()
  const mediaStreamDestination = audioContext.createMediaStreamDestination()
  const mediaRecorder = new MediaRecorder(mediaStreamDestination.stream)
  const chunks: BlobPart[] = []

  mediaRecorder.ondataavailable = (e) => chunks.push(e.data)
  mediaRecorder.onstop = () => {
    const blob = new Blob(chunks, { type: "audio/wav" })
    const url = URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = filename
    a.click()
    URL.revokeObjectURL(url)
  }

  mediaRecorder.start()
  window.speechSynthesis.speak(utterance)

  utterance.onend = () => {
    mediaRecorder.stop()
  }
}
