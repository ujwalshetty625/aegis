import uuid
import datetime
from typing import Any, Dict


def create_review_case(
    cursor: Any,
    *,
    user_id: str,
    account_id: str,
    decision: str,
    risk_score: float,
) -> Dict[str, Any]:
    """
    Create a fraud analyst review case for a given account.
    """
    case_id = str(uuid.uuid4())
    now = datetime.datetime.utcnow()

    cursor.execute(
        """
        INSERT INTO review_cases (
            case_id,
            user_id,
            account_id,
            decision,
            risk_score,
            status,
            created_at
        )
        VALUES (%s, %s, %s, %s, %s, 'OPEN', %s)
        """,
        (
            case_id,
            user_id,
            account_id,
            decision,
            risk_score,
            now,
        ),
    )

    return {
        "case_id": case_id,
        "user_id": user_id,
        "account_id": account_id,
        "decision": decision,
        "risk_score": risk_score,
        "status": "OPEN",
        "created_at": now,
    }

