const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

export async function fetchMetrics() {
  const res = await fetch(`${BASE_URL}/metrics/overview`, {
    cache: "no-store",
  });
  if (!res.ok) throw new Error("Failed to load metrics");
  return res.json();
}

export async function fetchOpenCases() {
  const res = await fetch(`${BASE_URL}/cases/open`, {
    cache: "no-store",
  });
  if (!res.ok) throw new Error("Failed to load cases");
  return res.json();
}


export async function fetchAccountProfile(accountId: string) {
  const res = await fetch(`${BASE_URL}/accounts/${accountId}/profile`, {
    cache: "no-store",
  });

  return res.json();
}


export async function resolveCase(
  caseId: string,
  analystNote: string,
  resolution: "ALLOW" | "BLOCK" | "ESCALATE" = "ALLOW"
) {
  const res = await fetch(`${BASE_URL}/cases/${caseId}/resolve`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ analyst_note: analystNote, resolution }),
  });

  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body?.detail || `Resolve failed (${res.status})`);
  }
  return res.json();
}

export async function fetchLatestDecisions() {
  const res = await fetch(`${BASE_URL}/decisions/latest`, {
    cache: "no-store",
  });
  if (!res.ok) throw new Error("Failed to load latest decisions");
  return res.json();
}

export async function fetchAccounts() {
  const res = await fetch(`${BASE_URL}/accounts`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to list accounts");
  return res.json();
}

export async function fetchTransactions(accountId: string) {
  const res = await fetch(`${BASE_URL}/accounts/${accountId}/transactions`, {
    cache: "no-store",
  });
  if (!res.ok) throw new Error("Failed to fetch transactions");
  return res.json();
}

export async function fetchAudit(accountId: string) {
  const res = await fetch(`${BASE_URL}/accounts/${accountId}/audit`, {
    cache: "no-store",
  });
  if (res.status === 404) return { audit_history: [] };
  if (!res.ok) throw new Error("Failed to fetch audit");
  return res.json();
}

export async function fetchSystemHealth() {
  const res = await fetch(`${BASE_URL}/system/health/deep`, {
    cache: "no-store",
  });
  if (!res.ok) throw new Error("Failed to fetch system health");
  return res.json();
}

export async function injectTransaction(data: {
  account_id: string
  amount: number
  device_id: string
}) {
  const res = await fetch(`${BASE_URL}/transactions`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  })

  if (!res.ok) {
    const err = await res.text()
    throw new Error(err)
  }

  return res.json()
}

export async function createAccount(payload: {
  name: string;
  email: string;
  phone: string;
}) {
  const res = await fetch(`${BASE_URL}/accounts/create`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    const errorBody = await res.json().catch(() => ({}));
    throw new Error(errorBody?.detail || `Create account failed (${res.status})`);
  }

  return res.json();
}


export async function getAccountDetails(accountId: string) {
  const res = await fetch(`${BASE_URL}/accounts/${accountId}`, { cache: "no-store" });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body?.detail || "Account not found");
  }
  return res.json();
}


export async function explainTransaction(txnId: string) {
  const res = await fetch(`${BASE_URL}/transactions/${txnId}/explain`, {
    cache: "no-store",
  });
  if (!res.ok) throw new Error("Failed to explain transaction");
  return res.json();
}

export async function fetchAuditIntegrity() {
  const res = await fetch(`${BASE_URL}/audit/integrity`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch audit integrity");
  return res.json();
}

export async function fetchDeepHealth() {
  const res = await fetch(`${BASE_URL}/system/health/deep`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch system health");
  return res.json();
}

export async function fetchAccountSignals(accountId: string) {
  const res = await fetch(
    `${BASE_URL}/accounts/${accountId}/signals`,
    { cache: "no-store" }
  );
  if (!res.ok) throw new Error("Failed to fetch signals");
  return res.json();
}

export async function fetchRiskTrend(accountId: string) {
  const res = await fetch(
    `${BASE_URL}/accounts/${accountId}/risk-trend`,
    { cache: "no-store" }
  );

  if (!res.ok) {
    throw new Error("Failed to fetch risk trend");
  }

  return res.json();
}