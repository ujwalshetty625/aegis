"use client";

import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { fetchAccountProfile } from "@/lib/api";

export default function AccountInvestigationPage() {
  const params = useParams();
  const accountId = params?.accountId as string;

  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function load() {
    try {
      setLoading(true);
      setError(null);

      const res = await fetchAccountProfile(accountId);

      setData(res);
    } catch (err: any) {
      console.error(err);
      setError(err?.message || "Failed to load account profile");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    if (accountId) load();
  }, [accountId]);

  if (loading) {
    return <div className="p-10 text-gray-400 font-mono">Loading...</div>;
  }

  if (error) {
    return <div className="p-10 text-red-400 font-mono">Error: {error}</div>;
  }

  const account = data?.account;
  const transactions = data?.recent_transactions || [];
  const signals = data?.recent_signals || [];
  const decision = data?.latest_decision;
  const openCase = data?.open_case;

  return (
    <main className="p-10 space-y-10 text-white">

      <h1 className="text-2xl font-bold">Account Investigation</h1>

      {/* Account Summary */}
      <div className="bg-[#0D1117] border border-[#1C2630] rounded-xl p-6 space-y-2">
        <p className="font-mono text-xs text-gray-400">Account ID</p>
        <p className="font-mono text-sky-400">{account?.account_id}</p>

        <p className="font-mono text-xs text-gray-400">Balance</p>
        <p className="font-mono">₹{account?.balance}</p>

        <p className="font-mono text-xs text-gray-400">Status</p>
        <p className="font-mono">{account?.status}</p>
      </div>

      {/* Latest Decision */}
      {decision && (
        <div className="bg-[#0D1117] border border-[#1C2630] rounded-xl p-6">
          <h2 className="text-sm font-mono text-gray-400 mb-3">
            Latest Risk Decision
          </h2>

          <div className="flex justify-between font-mono text-sm">
            <span>Decision</span>
            <span
              className={
                decision.decision === "BLOCK"
                  ? "text-red-400"
                  : decision.decision === "REVIEW"
                  ? "text-yellow-400"
                  : "text-green-400"
              }
            >
              {decision.decision}
            </span>
          </div>

          <div className="flex justify-between font-mono text-sm">
            <span>Risk Score</span>
            <span>{decision.risk_score}</span>
          </div>

          <p className="text-xs text-gray-400 mt-3">{decision.reasons}</p>
        </div>
      )}

      {/* Transactions */}
      <div className="bg-[#0D1117] border border-[#1C2630] rounded-xl p-6">
        <h2 className="text-sm font-mono text-gray-400 mb-4">
          Recent Transactions
        </h2>

        {transactions.length ? (
          transactions.map((t: any) => (
            <div
              key={t.txn_id}
              className="flex justify-between font-mono text-xs border-b border-[#1C2630] py-2"
            >
              <span>{t.txn_id}</span>
              <span>₹{t.amount}</span>
              <span>{t.status}</span>
            </div>
          ))
        ) : (
          <p className="text-gray-500 text-xs font-mono">
            No transactions found.
          </p>
        )}
      </div>

      {/* Signals */}
      <div className="bg-[#0D1117] border border-[#1C2630] rounded-xl p-6">
        <h2 className="text-sm font-mono text-gray-400 mb-4">
          Recent Risk Signals
        </h2>

        {signals.length ? (
          signals.map((s: any, i: number) => (
            <div
              key={i}
              className="border-b border-[#1C2630] py-2 text-xs font-mono"
            >
              <p className="text-yellow-400">{s.signal_type}</p>
              <p className="text-gray-400">{s.description}</p>
            </div>
          ))
        ) : (
          <p className="text-gray-500 text-xs font-mono">
            No signals detected.
          </p>
        )}
      </div>

      {/* Case */}
      {openCase && (
        <div className="bg-[#0D1117] border border-[#1C2630] rounded-xl p-6">
          <h2 className="text-sm font-mono text-gray-400 mb-4">
            Open Case
          </h2>

          <p className="font-mono text-xs">
            Case ID: {openCase.case_id}
          </p>
          <p className="font-mono text-xs">
            Decision: {openCase.decision}
          </p>
          <p className="font-mono text-xs">
            Risk Score: {openCase.risk_score}
          </p>
        </div>
      )}

    </main>
  );
}