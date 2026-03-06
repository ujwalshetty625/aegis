"use client";

import { useState } from "react";
import { injectTransaction } from "@/lib/api";

interface InjectResult {
  transaction_id?: string;
  decision?: "ALLOW" | "REVIEW" | "BLOCK";
  risk_score?: number;
  decision_latency_ms?: number;
}

type Props = {
  onAfterInject?: () => void | Promise<void>;
};

export default function TransactionSimulator({ onAfterInject }: Props) {
  const [accountId, setAccountId] = useState<string>("");
  const [amount, setAmount] = useState<string>("");
  const [deviceId, setDeviceId] = useState<string>("");

  const [loading, setLoading] = useState<boolean>(false);
  const [result, setResult] = useState<InjectResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();

    if (!accountId.trim()) {
      setError("Account ID is required");
      return;
    }

    if (!amount || Number(amount) <= 0) {
      setError("Amount must be greater than 0");
      return;
    }

    if (!deviceId.trim()) {
      setError("Device ID is required");
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const res = await injectTransaction({
        account_id: accountId.trim(),
        amount: Number(amount),
        device_id: deviceId.trim(),
      });

      setResult(res);

      if (onAfterInject) {
        await onAfterInject();
      }
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("Transaction failed");
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-6">
      <h2 className="text-sm font-mono text-gray-400 uppercase">
        Transaction Simulator
      </h2>

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Account ID */}
        <div>
          <label className="text-xs font-mono text-gray-400 block mb-1">
            Account ID
          </label>
          <input
            value={accountId}
            onChange={(e) => setAccountId(e.target.value)}
            placeholder="Paste account ID"
            className="w-full bg-[#05070A] border border-[#1C2630] rounded-lg px-3 py-2 text-sm font-mono"
            required
          />
        </div>

        {/* Amount + Device */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="text-xs font-mono text-gray-400 block mb-1">
              Amount (₹)
            </label>
            <input
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              placeholder="1000"
              type="number"
              min={1}
              className="w-full bg-[#05070A] border border-[#1C2630] rounded-lg px-3 py-2 text-sm font-mono"
              required
            />
          </div>

          <div>
            <label className="text-xs font-mono text-gray-400 block mb-1">
              Device ID
            </label>
            <input
              value={deviceId}
              onChange={(e) => setDeviceId(e.target.value)}
              placeholder="device_1"
              className="w-full bg-[#05070A] border border-[#1C2630] rounded-lg px-3 py-2 text-sm font-mono"
              required
            />
          </div>
        </div>

        {/* Button */}
        <button
          type="submit"
          disabled={loading}
          className="w-full bg-sky-600 hover:bg-sky-500 disabled:opacity-50 text-xs font-mono px-4 py-2 rounded-lg"
        >
          {loading ? "Processing..." : "Inject Transaction"}
        </button>
      </form>

      {/* Error */}
      {error && (
        <div className="text-red-400 text-xs font-mono bg-red-900/30 border border-red-700 rounded-lg px-3 py-2">
          {error}
        </div>
      )}

      {/* Result */}
      {result && (
        <div className="bg-[#05070A] border border-[#1C2630] rounded-lg p-4 text-xs font-mono space-y-2">
          <div className="flex justify-between">
            <span className="text-gray-400">Decision</span>
            <span
              className={
                result.decision === "BLOCK"
                  ? "text-red-400"
                  : result.decision === "REVIEW"
                  ? "text-amber-400"
                  : "text-green-400"
              }
            >
              {result.decision ?? "—"}
            </span>
          </div>

          <div className="flex justify-between">
            <span className="text-gray-400">Risk Score</span>
            <span>{(result.risk_score ?? 0).toFixed(2)}</span>
          </div>

          <div className="flex justify-between">
            <span className="text-gray-400">Latency (ms)</span>
            <span>{result.decision_latency_ms ?? "—"}</span>
          </div>
        </div>
      )}
    </div>
  );
}