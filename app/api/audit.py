from fastapi import APIRouter, HTTPException, Query

from app.data.database import get_connection
from app.audit.queries import fetch_account_audit

router = APIRouter(prefix="/accounts", tags=["Audit Traceability"])


@router.get("/{account_id}/audit")
def get_account_audit(
    account_id: str,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    """
    Full audit trace endpoint.

    Returns:
    - All SIGNAL_GENERATED events
    - All DECISION_MADE events
    For compliance + analyst investigation.
    """

    conn = get_connection()
    cursor = conn.cursor()

    audit_events = fetch_account_audit(
        cursor,
        account_id,
        limit=limit,
        offset=offset,
    )

    if not audit_events:
        raise HTTPException(
            status_code=404,
            detail=f"No audit history found for account_id={account_id}",
        )

    return {
        "account_id": account_id,
        "limit": limit,
        "offset": offset,
        "returned_events": len(audit_events),
        "audit_history": audit_events,
    }
