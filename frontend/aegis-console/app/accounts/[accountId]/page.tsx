"use client";

import RiskGauge from "@/components/ui/RiskGauge";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { fetchRiskTrend } from "@/lib/api";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid
} from "recharts";

export default function AccountProfilePage() {
  const params = useParams();
  const accountId = params.accountId as string;

  const [data, setData] = useState<any>(null);
  const [riskTrend, setRiskTrend] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  async function loadProfile() {
    try {
      setLoading(true);

      const res = await fetch(
        `http://127.0.0.1:8000/accounts/${accountId}/profile`
      );

      const json = await res.json();
      setData(json);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  async function loadTrend() {
    try {
      const trend = await fetchRiskTrend(accountId);
      setRiskTrend(Array.isArray(trend) ? trend : []);
    } catch (err) {
      console.error("Trend fetch failed", err);
      setRiskTrend([]);
    }
  }

  useEffect(() => {
    if (accountId) {
      loadProfile();
      loadTrend();
    }
  }, [accountId]);

  if (loading) {
    return <p className="p-10">Loading account profile...</p>;
  }

  if (!data || data.detail) {
    return (
      <p className="p-10 text-red-600">
        Error: {data?.detail ?? "Unknown error"}
      </p>
    );
  }

  const latest = data.latest_decision;
  const openCase = data.open_case;

  const caseAgeHours =
    openCase?.created_at
      ? (Date.now() - new Date(openCase.created_at).getTime()) / 3600000
      : 0;

  return (
    <main className="min-h-screen bg-[#080C0F] text-white p-10 space-y-10">
      {/* HEADER */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold font-mono">
            Account Investigation
          </h1>
          <p className="text-xs text-gray-400 font-mono">
            Account ID: {accountId}
          </p>
        </div>

        {latest && (
          <div
            className={`px-4 py-2 rounded-full border text-xs font-mono ${
              latest.decision === "BLOCK"
                ? "bg-red-500/10 text-red-400 border-red-500/30"
                : latest.decision === "REVIEW"
                ? "bg-amber-500/10 text-amber-400 border-amber-500/30"
                : "bg-green-500/10 text-green-400 border-green-500/30"
            }`}
          >
            {latest.decision}
          </div>
        )}
      </div>

      {latest && (
        <>
          {/* GRID */}
          <div className="grid grid-cols-3 gap-8">
            <RiskGauge score={Number(latest.risk_score) || 0} />

            <div className="col-span-2 space-y-6">
              {/* DECISION DETAILS */}
              <div className="bg-[#0D1117] border border-[#1C2630] rounded-xl p-6">
                <h2 className="text-sm font-mono text-gray-400 uppercase mb-4">
                  Latest Risk Decision
                </h2>

                <div className="space-y-3 text-sm">
                  <p>
                    <span className="text-gray-400 font-mono">
                      Risk Score:
                    </span>{" "}
                    <span className="font-mono">
                      {Number(latest.risk_score).toFixed(2)}
                    </span>
                  </p>

                  <p>
                    <span className="text-gray-400 font-mono">
                      Decision Timestamp:
                    </span>{" "}
                    {latest.created_at
                      ? new Date(latest.created_at).toLocaleString()
                      : "N/A"}
                  </p>

                  <p className="whitespace-pre-wrap text-gray-300">
                    <span className="text-gray-400 font-mono">
                      Reasons:
                    </span>{" "}
                    {latest.reasons || "N/A"}
                  </p>
                </div>
              </div>

              {/* EXPLAINABLE SIGNALS */}
              <div className="bg-[#0D1117] border border-[#1C2630] rounded-xl p-6">
                <h2 className="text-sm font-mono text-gray-400 uppercase mb-4">
                  Explainable Signal Contributions
                </h2>

                {Array.isArray(data.recent_signals) &&
                data.recent_signals.length > 0 ? (
                  data.recent_signals.map((s: any, i: number) => {
                    const contribution =
                      Number(s.signal_contribution) || 0;
                    const totalScore =
                      Number(latest.risk_score) || 1;

                    const percent =
                      totalScore > 0
                        ? (contribution / totalScore) * 100
                        : 0;

                    return (
                      <div key={i} className="space-y-2 mb-5">
                        <div className="flex justify-between text-xs font-mono text-gray-400">
                          <span>{s.signal_type}</span>
                          <span>{contribution.toFixed(2)} pts</span>
                        </div>

                        <div className="h-2 bg-[#111820] rounded-full overflow-hidden">
                          <div
                            className="h-full bg-blue-500"
                            style={{
                              width: `${Math.min(percent, 100)}%`,
                            }}
                          />
                        </div>

                        <div className="text-xs font-mono text-gray-500">
                          Weight: {s.signal_weight ?? "N/A"} | Value:{" "}
                          {s.signal_value ?? "N/A"}
                        </div>
                      </div>
                    );
                  })
                ) : (
                  <p className="text-gray-400 text-sm">
                    No recent signals found.
                  </p>
                )}
              </div>
            </div>
          </div>

          {/* RISK TREND */}
          <div className="bg-[#0D1117] border border-[#1C2630] rounded-xl p-6">
            <h2 className="text-sm font-mono text-gray-400 uppercase mb-6">
              Risk Trend
            </h2>

            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={riskTrend}>
                  <CartesianGrid stroke="#1C2630" />
                  <XAxis
                    dataKey="timestamp"
                    tick={{ fill: "#6B7280", fontSize: 10 }}
                    tickFormatter={(value) =>
                      value
                        ? new Date(value).toLocaleTimeString()
                        : ""
                    }
                  />
                  <YAxis
                    domain={[0, 100]}
                    tick={{ fill: "#6B7280", fontSize: 10 }}
                  />
                  <Tooltip />
                  <Line
                    type="monotone"
                    dataKey="risk_score"
                    stroke="#3B82F6"
                    strokeWidth={2}
                    dot={false}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* OPEN CASE */}
          <div
            className={`bg-[#0D1117] border rounded-xl p-6 ${
              caseAgeHours > 24
                ? "border-red-500"
                : "border-[#1C2630]"
            }`}
          >
            <h2 className="text-sm font-mono text-gray-400 uppercase mb-4">
              Open Review Case
            </h2>

            {openCase ? (
              <div className="font-mono text-sm space-y-2">
                <p>
                  Case ID: {openCase.case_id} — {openCase.status}
                </p>
                <p className="text-gray-400">
                  Age: {caseAgeHours.toFixed(1)} hours
                </p>
                {caseAgeHours > 24 && (
                  <p className="text-red-400 text-xs">
                    SLA BREACH — Case exceeds 24h threshold
                  </p>
                )}
              </div>
            ) : (
              <p className="text-gray-400 text-sm">
                No open case.
              </p>
            )}
          </div>
        </>
      )}
    </main>
  );
}