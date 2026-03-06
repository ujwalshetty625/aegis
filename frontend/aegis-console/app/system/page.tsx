"use client";

import { useEffect, useState } from "react";
import { fetchSystemHealth } from "@/lib/api";

export default function SystemPage() {
  const [health, setHealth] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function load() {
    setLoading(true);
    setError(null);
    try {
      const h = await fetchSystemHealth();
      setHealth(h);
    } catch (err: any) {
      setError(err.message || "Failed to load system health");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  if (loading && !health) {
    return (
      <main className="p-10 min-h-screen text-gray-400">
        Loading system health...
      </main>
    );
  }

  const ok = (v: boolean) => (v ? "text-green-400" : "text-red-400");

  return (
    <main className="p-10 space-y-10 min-h-screen text-white">
      <h1 className="text-3xl font-bold">System Health</h1>
      {error && (
        <div className="px-3 py-2 rounded-md bg-red-900/40 border border-red-700 text-xs text-red-200 font-mono">
          {error}
        </div>
      )}

      <div className="space-y-4">
        <div className="flex items-center gap-3">
          <span className="font-mono text-sm">Database:</span>
          <span className={ok(health?.database)}>
            {health?.database ? "Healthy" : "Unhealthy"}
          </span>
        </div>
        <div className="flex items-center gap-3">
          <span className="font-mono text-sm">Audit Chain Valid:</span>
          <span className={ok(health?.audit_chain_valid)}>
            {health?.audit_chain_valid ? "Yes" : "No"}
          </span>
        </div>
        <div>
          <p className="font-mono text-sm text-gray-400 mb-2">Tables:</p>
          <div className="flex flex-wrap gap-2">
            {health?.tables &&
              Object.entries(health.tables).map(([name, exists]: [string, any]) => (
                <span
                  key={name}
                  className={`font-mono text-xs px-2 py-1 rounded ${exists ? "bg-green-900/40 text-green-300" : "bg-red-900/40 text-red-300"}`}
                >
                  {name}: {exists ? "OK" : "MISSING"}
                </span>
              ))}
          </div>
        </div>
      </div>
    </main>
  );
}
