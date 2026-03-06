export default function DecisionBadge({
  decision,
}: {
  decision: "ALLOW" | "REVIEW" | "BLOCK"
}) {
  const styles = {
    ALLOW: "bg-green-100 text-green-800",
    REVIEW: "bg-yellow-100 text-yellow-800",
    BLOCK: "bg-red-100 text-red-800",
  }

  return (
    <span
      className={`px-3 py-1 rounded-full text-xs font-semibold ${styles[decision]}`}
    >
      {decision}
    </span>
  )
}
