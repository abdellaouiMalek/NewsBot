import { CircularProgressbar, buildStyles } from "react-circular-progressbar"
import "react-circular-progressbar/dist/styles.css"

interface TrustRatingIndicatorProps {
  score: number
}

export function TrustRatingIndicator({ score }: TrustRatingIndicatorProps) {
  const getColor = (score: number) => {
    if (score >= 80) return "#10b981" // green
    if (score >= 60) return "#f59e0b" // amber
    return "#ef4444" // red
  }

  return (
    <div className="w-24 h-24 flex-shrink-0">
      <CircularProgressbar
        value={score}
        text={`${score}%`}
        styles={buildStyles({
          rotation: 0,
          strokeLinecap: "round",
          textSize: "24px",
          pathTransitionDuration: 0.5,
          pathColor: getColor(score),
          textColor: getColor(score),
          trailColor: "#e5e7eb",
          backgroundColor: "#f3f4f6",
        })}
      />
      <p className="text-center text-xs font-semibold mt-2 text-muted-foreground">Trust Score</p>
    </div>
  )
}
