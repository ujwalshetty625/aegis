import uuid
import datetime
from typing import Any, Dict, Optional, Tuple


def fetch_latest_decision(cursor: Any, *, account_id: str) -> Optional[Tuple[float, str]]:
    """
    Fetch the most recent decision for an account, if any.
    """
    cursor.execute(
        """
        SELECT risk_score, decision
        FROM risk_decisions
        WHERE account_id = %s
        ORDER BY created_at DESC
        LIMIT 1
        """,
        (account_id,),
    )
    row = cursor.fetchone()
    if not row:
        return None
    return row["risk_score"], row["decision"]


def insert_decision(
    cursor: Any,
    *,
    user_id: str,
    account_id: str,
    risk_score: float,
    decision: str,
    reasons: str,
) -> Dict[str, Any]:
    """
    Persist a risk decision for an (account, user) pair.
    """
    decision_id = str(uuid.uuid4())
    now = datetime.datetime.utcnow()

    cursor.execute(
        """
        INSERT INTO risk_decisions
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
        (
            decision_id,
            user_id,
            account_id,
            risk_score,
            decision,
            reasons,
            now,
        ),
    )

    return {
        "decision_id": decision_id,
        "user_id": user_id,
        "account_id": account_id,
        "risk_score": risk_score,
        "decision": decision,
        "reasons": reasons,
        "created_at": now,
    }

def fetch_risk_trend(cursor, account_id: str, limit: int = 20):
    cursor.execute(
        """
        SELECT created_at, risk_score, decision
        FROM risk_decisions
        WHERE account_id = %s
        ORDER BY created_at DESC
        LIMIT %s
        """,
        (account_id, limit),
    )
    rows = cursor.fetchall()
    return list(reversed(rows))
