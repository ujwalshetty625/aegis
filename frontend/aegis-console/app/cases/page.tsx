"use client";

import { useEffect, useState } from "react";
import { fetchOpenCases, resolveCase } from "@/lib/api";

export default function CasesPage() {
  const [cases, setCases] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [resolving, setResolving] = useState<string | null>(null);
  const [note, setNote] = useState<Record<string, string>>({});

  async function load() {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchOpenCases();
      setCases(data.cases || []);
    } catch (err: any) {
      setError(err.message || "Failed to load cases");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function handleResolve(caseId: string, resolution: "ALLOW" | "BLOCK" | "ESCALATE") {
    const analystNote = note[caseId] || "Resolved via console";
    setResolving(caseId);
    setError(null);
    try {
      await resolveCase(caseId, analystNote, resolution);
      await load();
    } catch (err: any) {
      setError(err.message || "Failed to resolve case");
    } finally {
      setResolving(null);
    }
  }

  if (loading) {
    return (
      <main className="p-10 min-h-screen text-gray-400">
        Loading cases...
      </main>
    );
  }

  return (
    <main className="p-10 space-y-10 min-h-screen text-white">
      <h1 className="text-3xl font-bold">Review Queue</h1>
      {error && (
        <div className="px-3 py-2 rounded-md bg-red-900/40 border border-red-700 text-xs text-red-200 font-mono">
          {error}
        </div>
      )}

      <div className="bg-[#0D1117] border border-[#1C2630] rounded-xl overflow-hidden">
        <table className="w-full text-sm aegis-table">
          <thead>
            <tr className="border-b border-[#1C2630]">
              <th className="text-left py-2 px-2">Case ID</th>
              <th className="text-left py-2 px-2">Account ID</th>
              <th className="text-left py-2 px-2">Decision</th>
              <th className="text-right py-2 px-2">Risk Score</th>
              <th className="text-left py-2 px-2">Created At</th>
              <th className="text-left py-2 px-2">Note</th>
              <th className="text-left py-2 px-2">Actions</th>
            </tr>
          </thead>
          <tbody>
            {cases.map((c) => (
              <tr key={c.case_id} className="border-b border-[#1C2630]">
                <td className="py-2 px-2 font-mono text-xs">{c.case_id}</td>
                <td className="py-2 px-2 font-mono text-xs text-sky-400">
                  {c.account_id}
                </td>
                <td className="py-2 px-2 font-mono text-xs">{c.decision}</td>
                <td className="py-2 px-2 font-mono text-xs text-right">
                  {c.risk_score}
                </td>
                <td className="py-2 px-2 font-mono text-xs text-gray-400">
                  {c.created_at ? new Date(c.created_at).toLocaleString() : "—"}
                </td>
                <td className="py-2 px-2">
                  <input
                    type="text"
                    placeholder="Analyst note"
                    value={note[c.case_id] || ""}
                    onChange={(e) =>
                      setNote((n) => ({ ...n, [c.case_id]: e.target.value }))
                    }
                    className="w-40 bg-[#05070A] border border-[#1C2630] rounded px-2 py-1 text-xs font-mono"
                  />
                </td>
                <td className="py-2 px-2 flex gap-2">
                  <button
                    onClick={() => handleResolve(c.case_id, "ALLOW")}
                    disabled={!!resolving}
                    className="bg-green-600 hover:bg-green-500 disabled:opacity-50 text-xs font-mono px-2 py-1 rounded"
                  >
                    Approve
                  </button>
                  <button
                    onClick={() => handleResolve(c.case_id, "BLOCK")}
                    disabled={!!resolving}
                    className="bg-red-600 hover:bg-red-500 disabled:opacity-50 text-xs font-mono px-2 py-1 rounded"
                  >
                    Block
                  </button>
                  <button
                    onClick={() => handleResolve(c.case_id, "ESCALATE")}
                    disabled={!!resolving}
                    className="bg-amber-600 hover:bg-amber-500 disabled:opacity-50 text-xs font-mono px-2 py-1 rounded"
                  >
                    Escalate
                  </button>
                </td>
              </tr>
            ))}
            {cases.length === 0 && (
              <tr>
                <td colSpan={7} className="py-8 text-center text-gray-500 text-sm">
                  No open cases.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </main>
  );
}
