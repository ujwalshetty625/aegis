export default function RiskBadge({ score }: { score: number }) {
  type Level = "high" | "medium" | "low"

  let level: Level = "low"
  if (score >= 70) level = "high"
  else if (score >= 40) level = "medium"

  const styles: Record<Level, string> = {
    high: "bg-[rgba(239,68,68,0.1)] text-red-500 border border-[rgba(239,68,68,0.25)] glow-red",
    medium: "bg-[rgba(245,158,11,0.1)] text-amber-500 border border-[rgba(245,158,11,0.25)] glow-amber",
    low: "bg-[rgba(16,185,129,0.1)] text-green-500 border border-[rgba(16,185,129,0.25)] glow-green",
  }

  return (
    <span className={`px-3 py-1 text-xs font-mono font-semibold rounded-md ${styles[level]}`}>
      {score}
    </span>
  )
}