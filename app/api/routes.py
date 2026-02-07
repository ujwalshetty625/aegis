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
        LIMIT ?
    """, (limit,))

    rows = cursor.fetchall()
    conn.close()

    return {
        "count": len(rows),
        "signals": [
            {
                "signal_id": r[0],
                "user_id": r[1],
                "type": r[2],
                "value": r[3],
                "description": r[4],
                "created_at": r[5],
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
        LIMIT ?
    """, (limit,))

    rows = cursor.fetchall()
    conn.close()

    return {
        "count": len(rows),
        "decisions": [
            {
                "decision_id": r[0],
                "user_id": r[1],
                "account_id": r[2],
                "risk_score": r[3],
                "decision": r[4],
                "reasons": r[5],
                "created_at": r[6],
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
        WHERE account_id = ?
        ORDER BY created_at DESC
        LIMIT 1
    """, (account_id,))

    row = cursor.fetchone()
    conn.close()

    if not row:
        return {"error": "No decision found for this account"}

    return {
        "decision_id": row[0],
        "user_id": row[1],
        "account_id": row[2],
        "risk_score": row[3],
        "decision": row[4],
        "reasons": row[5],
        "created_at": row[6],
    }
