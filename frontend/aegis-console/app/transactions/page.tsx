"use client";

import { useState } from "react";
import { fetchTransactions } from "@/lib/api";

export default function TransactionsPage() {
  const [accountId, setAccountId] = useState("");
  const [txns, setTxns] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSearch(e: React.FormEvent) {
    e.preventDefault();

    const id = accountId.trim();
    if (!id) return;

    setLoading(true);
    setError(null);

    try {
      const data = await fetchTransactions(id);

      const list = Array.isArray(data)
        ? data
        : data?.transactions ?? [];

      setTxns(list);
    } catch (err: any) {
      setError(err.message || "Failed to fetch transactions");
      setTxns([]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="p-10 space-y-10 min-h-screen text-white">
      <h1 className="text-3xl font-bold">Transaction History</h1>

      <form onSubmit={handleSearch} className="flex gap-4 items-end">
        <div>
          <label className="text-xs text-gray-400 font-mono block mb-1">
            Account ID
          </label>

          <input
            type="text"
            value={accountId}
            onChange={(e) => setAccountId(e.target.value)}
            placeholder="Enter account ID"
            className="w-80 bg-[#0D1117] border border-[#1C2630] rounded-lg px-3 py-2 text-sm font-mono"
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          className="bg-sky-600 hover:bg-sky-500 disabled:opacity-50 text-xs font-mono px-4 py-2 rounded-lg"
        >
          {loading ? "Loading..." : "Search"}
        </button>
      </form>

      {error && (
        <div className="px-3 py-2 rounded-md bg-red-900/40 border border-red-700 text-xs text-red-200 font-mono">
          {error}
        </div>
      )}

      <div className="bg-[#0D1117] border border-[#1C2630] rounded-xl overflow-hidden">
        <table className="w-full text-sm aegis-table">
          <thead>
            <tr className="border-b border-[#1C2630]">
              <th className="text-left py-2 px-2">Txn ID</th>
              <th className="text-left py-2 px-2">Account ID</th>
              <th className="text-right py-2 px-2">Amount</th>
              <th className="text-left py-2 px-2">Device ID</th>
              <th className="text-left py-2 px-2">Timestamp</th>
              <th className="text-left py-2 px-2">Decision</th>
              <th className="text-right py-2 px-2">Risk Score</th>
            </tr>
          </thead>

          <tbody>
            {txns.map((t) => (
              <tr
                key={t.txn_id}
                className="border-b border-[#1C2630]"
              >
                <td className="py-2 px-2 font-mono text-xs truncate max-w-[140px]">
                  {t.txn_id ?? "—"}
                </td>

                <td className="py-2 px-2 font-mono text-xs text-sky-400 truncate max-w-[140px]">
                  {t.account_id ?? "—"}
                </td>

                <td className="py-2 px-2 font-mono text-xs text-right">
                  {t.amount != null
                    ? `₹${Number(t.amount).toFixed(2)}`
                    : "—"}
                </td>

                <td className="py-2 px-2 font-mono text-xs">
                  {t.device_id ?? "—"}
                </td>

                <td className="py-2 px-2 font-mono text-xs text-gray-400">
                  {t.timestamp
                    ? new Date(t.timestamp).toLocaleString("en-IN", {
                        timeZone: "Asia/Kolkata",
                      })
                    : "—"}
                </td>

                <td className="py-2 px-2 font-mono text-xs">
                  {t.decision ?? "—"}
                </td>

                <td className="py-2 px-2 font-mono text-xs text-right">
                  {t.risk_score != null
                    ? Number(t.risk_score).toFixed(2)
                    : "—"}
                </td>
              </tr>
            ))}

            {loading && txns.length === 0 && (
              <tr>
                <td
                  colSpan={7}
                  className="py-8 text-center text-gray-400 text-sm"
                >
                  Loading...
                </td>
              </tr>
            )}

            {!loading && txns.length === 0 && (
              <tr>
                <td
                  colSpan={7}
                  className="py-8 text-center text-gray-500 text-sm"
                >
                  Enter an account ID and click Search.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </main>
  );
}