"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { createAccount, fetchAccounts } from "@/lib/api";

export default function AccountsPage() {
  const router = useRouter();

  const [accounts, setAccounts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [createdAccountId, setCreatedAccountId] = useState<string | null>(null);

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");

  async function load() {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchAccounts();
      setAccounts(Array.isArray(data) ? data : []);
    } catch (err: any) {
      setError(err.message || "Failed to load accounts");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function onCreate(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setSuccess(null);
    setCreatedAccountId(null);

    try {
      setCreating(true);
      const res = await createAccount({ name, email, phone });

      setSuccess("Account created successfully.");
      setCreatedAccountId(res.account_id || null);

      setName("");
      setEmail("");
      setPhone("");

      await load();
    } catch (err: any) {
      setError(err.message || "Create account failed");
    } finally {
      setCreating(false);
    }
  }

  async function copyAccountId() {
    if (!createdAccountId) return;
    try {
      await navigator.clipboard.writeText(createdAccountId);
    } catch {
      /* ignore */
    }
  }

  return (
    <main className="space-y-8">
      <header className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Accounts</h1>
          <p className="text-xs text-gray-400 font-mono">
            Create and monitor customer accounts
          </p>
        </div>

        {error && (
          <div className="px-3 py-2 rounded-md bg-red-900/40 border border-red-700 text-xs text-red-200 font-mono">
            {error}
          </div>
        )}

        {success && (
          <div className="px-3 py-2 rounded-md bg-green-900/40 border border-green-700 text-xs text-green-200 font-mono space-y-2">
            <p>{success}</p>
            {createdAccountId && (
              <p className="flex items-center gap-2">
                <span>Account ID: {createdAccountId}</span>
                <button
                  type="button"
                  onClick={copyAccountId}
                  className="bg-green-800 hover:bg-green-700 px-2 py-0.5 rounded font-mono"
                >
                  Copy
                </button>
              </p>
            )}
          </div>
        )}
      </header>

      {/* Create Account */}
      <div className="aegis-card p-6">
        <h2 className="text-sm font-mono text-gray-400 uppercase mb-4">
          Create Account
        </h2>

        <form
          onSubmit={onCreate}
          className="grid grid-cols-4 gap-4 items-end"
        >
          <div>
            <label className="text-xs text-gray-400 font-mono mb-1 block">
              Name
            </label>
            <input
              className="w-full bg-[#05070A] border border-[#1C2630] rounded-lg px-3 py-2 text-sm font-mono focus:outline-none focus:ring-1 focus:ring-sky-500"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
            />
          </div>

          <div>
            <label className="text-xs text-gray-400 font-mono mb-1 block">
              Email
            </label>
            <input
              type="email"
              className="w-full bg-[#05070A] border border-[#1C2630] rounded-lg px-3 py-2 text-sm font-mono focus:outline-none focus:ring-1 focus:ring-sky-500"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>

          <div>
            <label className="text-xs text-gray-400 font-mono mb-1 block">
              Phone
            </label>
            <input
              className="w-full bg-[#05070A] border border-[#1C2630] rounded-lg px-3 py-2 text-sm font-mono focus:outline-none focus:ring-1 focus:ring-sky-500"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              required
            />
          </div>

          <button
            type="submit"
            disabled={creating}
            className="bg-sky-600 hover:bg-sky-500 disabled:bg-sky-900 text-xs font-mono px-4 py-2 rounded-lg"
          >
            {creating ? "Creating..." : "Create Account"}
          </button>
        </form>
      </div>

      {/* Accounts Table */}
      <div className="aegis-card p-6">
        <h2 className="text-sm font-mono text-gray-400 uppercase mb-4">
          Accounts
        </h2>

        <div className="overflow-x-auto">
          <table className="w-full text-sm aegis-table">
            <thead>
              <tr className="border-b border-[#1C2630]">
                <th className="text-left py-2 px-2">Account ID</th>
                <th className="text-left py-2 px-2">User ID</th>
                <th className="text-left py-2 px-2">Status</th>
                <th className="text-right py-2 px-2">Balance</th>
                <th className="text-left py-2 px-2">Created</th>
              </tr>
            </thead>

            <tbody>
              {accounts.map((a) => (
                <tr
                  key={a.account_id}
                  className="cursor-pointer hover:bg-[#0f141a]"
                  onClick={() => router.push(`/accounts/${a.account_id}`)}
                >
                  <td className="py-2 px-2 font-mono text-xs text-sky-400">
                    {a.account_id}
                  </td>

                  <td className="py-2 px-2 font-mono text-xs">
                    {a.user_id}
                  </td>

                  <td className="py-2 px-2 font-mono text-xs">
                    {a.status}
                  </td>

                  <td className="py-2 px-2 font-mono text-xs text-right">
                    ₹{Number(a.balance || 0).toFixed(2)}
                  </td>

                  <td className="py-2 px-2 font-mono text-xs text-gray-400">
                    {a.created_at
                      ? new Date(a.created_at).toLocaleString("en-IN", {
                          timeZone: "Asia/Kolkata",
                          dateStyle: "medium",
                          timeStyle: "short",
                        })
                      : "—"}
                  </td>
                </tr>
              ))}

              {loading && accounts.length === 0 && (
                <tr>
                  <td
                    colSpan={5}
                    className="py-8 text-center text-xs text-gray-400"
                  >
                    Loading...
                  </td>
                </tr>
              )}

              {!loading && accounts.length === 0 && (
                <tr>
                  <td
                    colSpan={5}
                    className="py-4 text-center text-xs text-gray-500"
                  >
                    No accounts found.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </main>
  );
}