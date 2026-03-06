from typing import Any

from app.repositories.case_repo import create_review_case as repo_create_review_case
from app.repositories.audit_repo import log_case_opened


def create_review_case(cursor: Any, user_id: int, account_id: int, decision: str, risk_score: float):
    """
    Adapter that preserves the original risk engine API while
    delegating writes to the repository layer.
    """
    case = repo_create_review_case(
        cursor,
        user_id=user_id,
        account_id=account_id,
        decision=decision,
        risk_score=risk_score,
    )

    log_case_opened(
        cursor,
        account_id=account_id,
        metadata={
            "case_id": case["case_id"],
            "decision": decision,
            "risk_score": risk_score,
            "status": case["status"],
        },
    )
