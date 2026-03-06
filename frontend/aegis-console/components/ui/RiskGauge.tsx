export default function RiskGauge({ score }: { score: number }) {
  const color =
    score >= 70 ? "#ef4444" :
    score >= 40 ? "#f59e0b" :
    "#10b981";

  const level =
    score >= 70 ? "HIGH RISK" :
    score >= 40 ? "MEDIUM RISK" :
    "LOW RISK";

  return (
    <div className="bg-[#0D1117] border border-[#1C2630] rounded-xl p-6 flex flex-col items-center">
      <div
        className="w-32 h-32 rounded-full flex items-center justify-center border-4"
        style={{ borderColor: color }}
      >
        <span className="text-3xl font-bold font-mono" style={{ color }}>
          {score}
        </span>
      </div>

      <p className="mt-4 text-xs font-mono text-gray-400">Risk Score</p>
      <p className="text-sm font-mono mt-1" style={{ color }}>
        {level}
      </p>
    </div>
  );
}