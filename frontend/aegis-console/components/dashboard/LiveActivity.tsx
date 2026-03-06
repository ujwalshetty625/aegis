"use client";

import { useEffect, useState } from "react";
import { fetchLatestDecisions } from "@/lib/api";

type Props = {
  refreshKey?: number;
};

export default function LiveActivity({ refreshKey }: Props) {
  const [activity, setActivity] = useState<any[]>([]);
  const [error, setError] = useState<string | null>(null);

  async function loadActivity() {
    setError(null);
    try {
      const latest = await fetchLatestDecisions();
      const decisions = latest?.decisions ?? [];
      if (process.env.NODE_ENV === "development") console.log("Latest decisions:", decisions);
      setActivity(Array.isArray(decisions) ? decisions : []);
    } catch (err: any) {
      setError(err.message || "Failed to load");
      setActivity([]);
    }
  }

  useEffect(() => {
    loadActivity();
    const interval = setInterval(loadActivity, 10000);
    return () => clearInterval(interval);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [refreshKey]);

  return (
    <div className="aegis-card rounded-xl p-6 space-y-6">
      <h2 className="text-sm font-mono text-gray-400 uppercase">
        Live Risk Activity
      </h2>

      <div className="space-y-4 max-h-64 overflow-y-auto">
        {error && (
          <p className="text-red-400 text-xs font-mono">{error}</p>
        )}
        {!error && activity.length === 0 ? (
          <p className="text-gray-400 text-sm">
            No recent decisions
          </p>
        ) : !error ? (
          activity.map((d: any, i: number) => {
            const decisionColor =
              d.decision === "BLOCK"
                ? "text-red-400"
                : d.decision === "REVIEW"
                ? "text-amber-400"
                : "text-green-400";

            return (
              <div
                key={i}
                className="flex justify-between items-center text-xs font-mono border-b border-[#1C2630] pb-2"
              >
                <div className="flex flex-col">
                  <span className="text-blue-400">
                    {d.account_id}
                  </span>
                  <span className={decisionColor}>
                    {d.decision}
                  </span>
                </div>

                <div className="text-gray-400 text-[11px]">
                  {d.created_at
                    ? new Date(d.created_at).toLocaleString("en-IN", {
                        timeZone: "Asia/Kolkata",
                      })
                    : "—"}
                </div>
              </div>
            );
          })
        ) : null}
      </div>
    </div>
  );
}