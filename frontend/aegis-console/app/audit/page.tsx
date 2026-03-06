"use client";

import { useState } from "react";
import { fetchAudit } from "@/lib/api";

export default function AuditPage() {
  const [accountId, setAccountId] = useState("");
  const [events, setEvents] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSearch(e: React.FormEvent) {
    e.preventDefault();
    if (!accountId.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const data = await fetchAudit(accountId.trim());
      setEvents(data.audit_history || []);
    } catch (err: any) {
      setError(err.message || "Failed to fetch audit");
      setEvents([]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="p-10 space-y-10 min-h-screen text-white">
      <h1 className="text-3xl font-bold">Audit Logs</h1>

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
              <th className="text-left py-2 px-2">Event Type</th>
              <th className="text-left py-2 px-2">Entity Type</th>
              <th className="text-left py-2 px-2">Entity ID</th>
              <th className="text-left py-2 px-2">Created At</th>
            </tr>
          </thead>
          <tbody>
            {events.map((e, i) => (
              <tr key={i} className="border-b border-[#1C2630]">
                <td className="py-2 px-2 font-mono text-xs">{e.event_type}</td>
                <td className="py-2 px-2 font-mono text-xs">{e.entity_type}</td>
                <td className="py-2 px-2 font-mono text-xs">{e.entity_id}</td>
                <td className="py-2 px-2 font-mono text-xs text-gray-400">
                  {e.created_at ? new Date(e.created_at).toLocaleString() : "—"}
                </td>
              </tr>
            ))}
            {events.length === 0 && !loading && (
              <tr>
                <td colSpan={4} className="py-8 text-center text-gray-500 text-sm">
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
