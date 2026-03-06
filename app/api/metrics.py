from fastapi import APIRouter
from app.data.database import get_connection

router = APIRouter(prefix="/metrics", tags=["Metrics"])


@router.get("/overview")
def get_overview_metrics():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) AS cnt FROM transactions")
    total_txns = cursor.fetchone()["cnt"]

    cursor.execute("SELECT COUNT(*) AS cnt FROM accounts")
    total_accounts = cursor.fetchone()["cnt"]

    cursor.execute("""
        SELECT COUNT(*) AS cnt
        FROM review_cases
        WHERE status = 'OPEN'
    """)
    open_cases = cursor.fetchone()["cnt"]

    cursor.execute("""
        SELECT decision, COUNT(*) AS cnt
        FROM risk_decisions
        GROUP BY decision
    """)
    decision_rows = cursor.fetchall()

    # Ensure stable contract with zeroed defaults
    decisions = {
        "ALLOW": 0,
        "REVIEW": 0,
        "BLOCK": 0,
    }
    for row in decision_rows:
        decision = row["decision"]
        count = row["cnt"]
        if decision in decisions:
            decisions[decision] = count

    cursor.execute("SELECT COALESCE(AVG(risk_score), 0) AS avg_score FROM risk_decisions;")
    avg_risk_score = float(cursor.fetchone()["avg_score"] or 0)

    conn.close()

    return {
        "total_transactions": total_txns,
        "total_accounts": total_accounts,
        "open_cases": open_cases,
        "decisions": decisions,
        # new contract fields for upgraded console
        "decision_distribution": decisions,
        "avg_risk_score": round(avg_risk_score, 2),
    }
