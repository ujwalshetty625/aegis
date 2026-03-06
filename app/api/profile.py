from fastapi import APIRouter, HTTPException
from app.data.database import get_connection
from app.repositories.decision_repo import fetch_risk_trend

router = APIRouter(prefix="/accounts", tags=["Account Profile"])


@router.get("/{account_id}/signals")
def get_account_signals(account_id: str, limit: int = 50):
    """Return signals used in decisions for explainable risk analysis."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT 1 FROM accounts WHERE account_id = %s LIMIT 1
        """,
        (account_id,),
    )
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Account not found")

    cursor.execute(
        """
        SELECT s.signal_type, s.signal_value, s.signal_weight, s.signal_contribution, s.created_at
        FROM signals s
        JOIN accounts a ON s.user_id = a.user_id
        WHERE a.account_id = %s
        ORDER BY s.created_at DESC
        LIMIT %s
        """,
        (account_id, limit),
    )
    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "signal_type": r["signal_type"],
            "signal_value": float(r["signal_value"] or 0),
            "signal_weight": float(r["signal_weight"] or 0),
            "signal_contribution": float(r["signal_contribution"] or 0),
        }
        for r in rows
    ]


@router.get("/{account_id}/risk-trend")
def get_risk_trend(account_id: str, limit: int = 20):
    conn = get_connection()
    cursor = conn.cursor()

    trend = fetch_risk_trend(cursor, account_id, limit=limit)

    conn.close()

    return [
        {
            "timestamp": row["created_at"],
            "risk_score": row["risk_score"],
            "decision": row["decision"],
        }
        for row in trend
    ]


@router.get("/{account_id}/profile")
def get_account_profile(account_id: str):
    conn = get_connection()
    cursor = conn.cursor()

    # 1) Latest decision ALWAYS (even if account row missing)
    cursor.execute(
        """
        SELECT decision, risk_score, reasons, created_at
        FROM risk_decisions
        WHERE account_id = %s
        ORDER BY created_at DESC
        LIMIT 1
        """,
        (account_id,),
    )
    latest_decision = cursor.fetchone()

    # 2) Account row (may be missing)
    cursor.execute(
        """
        SELECT account_id, user_id, account_type, balance, status, created_at
        FROM accounts
        WHERE account_id = %s
        LIMIT 1
        """,
        (account_id,),
    )
    acct = cursor.fetchone()

    # ✅ If account missing but decision exists → still return decision
    if not acct:
        conn.close()
        if latest_decision:
            return {
                "account": None,
                "latest_decision": dict(latest_decision),
                "recent_signals": [],
                "recent_transactions": [],
                "open_case": None,
                "warning": "Orphan account_id: decision exists but account row missing",
            }
        from fastapi import HTTPException  # local import to avoid circulars
        raise HTTPException(status_code=404, detail="Account not found")

    user_id = acct["user_id"]

    # 3) Signals (user-level)
    cursor.execute(
        """
        SELECT signal_type, signal_value, description, created_at
        FROM signals
        WHERE user_id = %s
        ORDER BY created_at DESC
        LIMIT 10
        """,
        (user_id,),
    )
    signals = cursor.fetchall()

    # 4) Transactions (account-level)
    cursor.execute(
        """
        SELECT txn_id, amount, merchant_category, location, txn_timestamp, status
        FROM transactions
        WHERE account_id = %s
        ORDER BY txn_timestamp DESC
        LIMIT 10
        """,
        (account_id,),
    )
    txns = cursor.fetchall()

    # 5) Open case
    cursor.execute(
        """
        SELECT case_id, decision, risk_score, status, created_at
        FROM review_cases
        WHERE account_id = %s
          AND status = 'OPEN'
        ORDER BY created_at DESC
        LIMIT 1
        """,
        (account_id,),
    )
    open_case = cursor.fetchone()

    conn.close()

    return {
        "account": dict(acct),
        "latest_decision": dict(latest_decision) if latest_decision else None,
        "recent_signals": [dict(s) for s in signals],
        "recent_transactions": [dict(t) for t in txns],
        "open_case": dict(open_case) if open_case else None,
    }
