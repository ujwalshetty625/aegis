from fastapi import APIRouter
from app.data.database import get_connection

router = APIRouter()


# -----------------------------
# Health Check
# -----------------------------
@router.get("/health")
def health():
    return {"status": "ok", "service": "aegis-risk-engine"}


# -----------------------------
# Recent Signals
# -----------------------------
@router.get("/signals/recent")
def recent_signals(limit: int = 20):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT signal_id, user_id, signal_type, signal_value, description, created_at
        FROM signals
        ORDER BY created_at DESC
        LIMIT %s
    """, (limit,))

    rows = cursor.fetchall()
    conn.close()

    return {
        "count": len(rows),
        "signals": [
            {
                "signal_id": r["signal_id"],
                "user_id": r["user_id"],
                "type": r["signal_type"],
                "value": r["signal_value"],
                "description": r["description"],
                "created_at": r["created_at"],
            }
            for r in rows
        ]
    }


# -----------------------------
# Latest Decisions
# -----------------------------
@router.get("/decisions/latest")
def latest_decisions(limit: int = 10):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT decision_id, user_id, account_id, risk_score, decision, reasons, created_at
        FROM risk_decisions
        ORDER BY created_at DESC
        LIMIT %s
    """, (limit,))

    rows = cursor.fetchall()
    conn.close()

    return {
        "count": len(rows),
        "decisions": [
            {
                "decision_id": r["decision_id"],
                "user_id": r["user_id"],
                "account_id": r["account_id"],
                "risk_score": r["risk_score"],
                "decision": r["decision"],
                "reasons": r["reasons"],
                "created_at": r["created_at"],
            }
            for r in rows
        ]
    }


# -----------------------------
# Account Risk Lookup
# -----------------------------
@router.get("/accounts/{account_id}/decision")
def account_decision(account_id: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT decision_id, user_id, account_id, risk_score, decision, reasons, created_at
        FROM risk_decisions
        WHERE account_id = %s
        ORDER BY created_at DESC
        LIMIT 1
    """, (account_id,))

    row = cursor.fetchone()
    conn.close()

    if not row:
        return {"error": "No decision found for this account"}

    return {
        "decision_id": row["decision_id"],
        "user_id": row["user_id"],
        "account_id": row["account_id"],
        "risk_score": row["risk_score"],
        "decision": row["decision"],
        "reasons": row["reasons"],
        "created_at": row["created_at"],
    }
