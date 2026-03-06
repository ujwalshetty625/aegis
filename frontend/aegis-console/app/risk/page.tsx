"use client";

import { useEffect, useState } from "react";
import { fetchMetrics } from "@/lib/api";

export default function RiskPage() {
  const [metrics, setMetrics] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function load() {
    setLoading(true);
    setError(null);
    try {
      const m = await fetchMetrics();
      setMetrics(m);
    } catch (err: any) {
      setError(err.message || "Failed to load metrics");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
    const interval = setInterval(load, 15000);
    return () => clearInterval(interval);
  }, []);

  if (loading && !metrics) {
    return (
      <main className="p-10 min-h-screen text-gray-400">
        Loading risk analytics...
      </main>
    );
  }

  const decisions = metrics?.decision_distribution ?? metrics?.decisions ?? {};
  const allow = decisions.ALLOW ?? 0;
  const review = decisions.REVIEW ?? 0;
  const block = decisions.BLOCK ?? 0;

  return (
    <main className="p-10 space-y-10 min-h-screen text-white">
      <h1 className="text-3xl font-bold">Risk Analytics</h1>
      {error && (
        <div className="px-3 py-2 rounded-md bg-red-900/40 border border-red-700 text-xs text-red-200 font-mono">
          {error}
        </div>
      )}

      <div className="grid grid-cols-4 gap-6">
        <div className="bg-[#0D1117] border border-[#1C2630] rounded-xl p-6">
          <p className="text-xs text-gray-400 font-mono uppercase">
            Total Transactions
          </p>
          <p className="text-3xl font-bold mt-2 font-mono">
            {metrics?.total_transactions ?? 0}
          </p>
        </div>
        <div className="bg-[#0D1117] border border-[#1C2630] rounded-xl p-6">
          <p className="text-xs text-gray-400 font-mono uppercase">
            Open Cases
          </p>
          <p className="text-3xl font-bold mt-2 font-mono text-amber-400">
            {metrics?.open_cases ?? 0}
          </p>
        </div>
        <div className="bg-[#0D1117] border border-[#1C2630] rounded-xl p-6">
          <p className="text-xs text-gray-400 font-mono uppercase">
            Avg Risk Score
          </p>
          <p className="text-3xl font-bold mt-2 font-mono text-sky-400">
            {(metrics?.avg_risk_score ?? 0).toFixed(2)}
          </p>
        </div>
      </div>

      <div className="bg-[#0D1117] border border-[#1C2630] rounded-xl p-8 space-y-6">
        <h2 className="text-sm font-mono text-gray-400 uppercase">
          Decision Distribution
        </h2>
        <div className="flex gap-4">
          <span className="font-mono text-sm">ALLOW: {allow}</span>
          <span className="font-mono text-sm">REVIEW: {review}</span>
          <span className="font-mono text-sm">BLOCK: {block}</span>
        </div>
      </div>
    </main>
  );
}
