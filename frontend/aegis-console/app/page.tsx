"use client";

import { useEffect, useState } from "react";
import { fetchMetrics } from "@/lib/api";
import LiveActivity from "../components/dashboard/LiveActivity";
import TransactionSimulator from "../components/dashboard/TransactionSimulator";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from "recharts";

type Metrics = {
  total_transactions: number;
  total_accounts?: number;
  open_cases: number;
  decision_distribution?: {
    ALLOW?: number;
    REVIEW?: number;
    BLOCK?: number;
  };
  avg_risk_score?: number;
};

export default function DashboardPage() {
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [refreshKey, setRefreshKey] = useState(0);

  async function loadMetrics() {
    setLoading(true);
    setError(null);
    try {
      const m = await fetchMetrics();
      if (process.env.NODE_ENV === "development") console.log("Metrics:", m);
      setMetrics(m);
    } catch (err: any) {
      setError(err.message || "Failed to load metrics");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadMetrics();
    const interval = setInterval(loadMetrics, 15000);
    return () => clearInterval(interval);
  }, []);

  const totalTx = metrics?.total_transactions ?? 0;
  const totalAccounts = metrics?.total_accounts ?? 0;
  const openCases = metrics?.open_cases ?? 0;
  const avgRisk = metrics?.avg_risk_score ?? 0;

  const decisions =
    metrics?.decision_distribution ?? metrics?.decisions ?? { ALLOW: 0, REVIEW: 0, BLOCK: 0 };
  const allow = decisions.ALLOW ?? 0;
  const review = decisions.REVIEW ?? 0;
  const block = decisions.BLOCK ?? 0;

  const totalDecisions = allow + review + block || 1;
  const distributionData = [
    { name: "ALLOW", count: allow },
    { name: "REVIEW", count: review },
    { name: "BLOCK", count: block },
  ];

  async function handleAfterInject() {
    await loadMetrics();
    setRefreshKey((k) => k + 1);
  }

  return (
    <main className="space-y-8">
      <header className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">
            Risk Command Center
          </h1>
          <p className="text-xs text-gray-400 font-mono">
            Live view of Aegis risk engine operations
          </p>
        </div>
        {error && (
          <div className="px-3 py-2 rounded-md bg-red-900/40 border border-red-700 text-xs text-red-200 font-mono">
            {error}
          </div>
        )}
      </header>

      {/* KPI Cards */}
      <div className="grid grid-cols-4 gap-6">
        <div className="aegis-card rounded-xl p-6">
          <p className="text-[11px] text-gray-400 font-mono uppercase">
            Total Accounts
          </p>
          <p className="text-3xl font-bold mt-2 font-mono">
            {loading && !metrics ? "…" : totalAccounts}
          </p>
        </div>

        <div className="aegis-card rounded-xl p-6">
          <p className="text-[11px] text-gray-400 font-mono uppercase">
            Total Transactions
          </p>
          <p className="text-3xl font-bold mt-2 font-mono">
            {loading && !metrics ? "…" : totalTx}
          </p>
        </div>

        <div className="aegis-card rounded-xl p-6">
          <p className="text-[11px] text-gray-400 font-mono uppercase">
            Open Cases
          </p>
          <p className="text-3xl font-bold mt-2 font-mono text-amber-400">
            {loading && !metrics ? "…" : openCases}
          </p>
        </div>

        <div className="aegis-card rounded-xl p-6">
          <p className="text-[11px] text-gray-400 font-mono uppercase">
            Avg Risk Score
          </p>
          <p className="text-3xl font-bold mt-2 font-mono text-sky-400">
            {avgRisk.toFixed(2)}
          </p>
        </div>
      </div>

      {/* Decision Distribution + Simulator */}
      <div className="grid grid-cols-2 gap-6">
        <div className="aegis-card rounded-xl p-6 space-y-4">
          <h2 className="text-sm font-mono text-gray-400 uppercase">
            Decision Distribution
          </h2>
          <div className="h-[280px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={distributionData}>
                <CartesianGrid stroke="#1C2630" vertical={false} />
                <XAxis dataKey="name" tick={{ fill: "#9CA3AF", fontSize: 11 }} />
                <YAxis tick={{ fill: "#9CA3AF", fontSize: 11 }} />
                <Tooltip />
                <Bar dataKey="count" fill="#0EA5E9" />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="flex justify-between text-xs font-mono text-gray-400">
            <span>ALLOW: {allow}</span>
            <span>REVIEW: {review}</span>
            <span>BLOCK: {block}</span>
          </div>
        </div>

        <div className="aegis-card rounded-xl p-6">
          <TransactionSimulator onAfterInject={handleAfterInject} />
        </div>
      </div>

      {/* Live activity full width */}
      <LiveActivity refreshKey={refreshKey} />
    </main>
  );
}