from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import datetime

from app.data.database import get_connection
from app.repositories.audit_repo import log_case_resolved

router = APIRouter(prefix="/cases", tags=["Cases"])


# ----------------------------
# Request Models
# ----------------------------

class ResolveCaseRequest(BaseModel):
    analyst_note: str
    resolution: str  # ALLOW / BLOCK / ESCALATE


# ----------------------------
# API: List Open Cases
# ----------------------------

@router.get("/open")
def get_open_cases(limit: int = 50):
    """
    Fraud Analyst Queue:
    Returns all OPEN review/block cases.
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT case_id, user_id, account_id,
               decision, risk_score,
               status, created_at
        FROM review_cases
        WHERE status = 'OPEN'
        ORDER BY created_at DESC
        LIMIT %s
    """, (limit,))

    rows = cursor.fetchall()
    conn.close()

    return {
        "returned": len(rows),
        "cases": [dict(r) for r in rows]
    }


@router.get("/{case_id}")
def get_case(case_id: str):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT *
            FROM review_cases
            WHERE case_id = %s
            LIMIT 1
            """,
            (case_id,),
        )
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Case not found")
        return dict(row)
    finally:
        conn.close()


# ----------------------------
# API: Resolve a Case
# ----------------------------

@router.post("/{case_id}/resolve")
def resolve_case(case_id: str, req: ResolveCaseRequest):
    """
    Analyst resolves a fraud review case.
    Marks case as RESOLVED + writes audit log.
    """

    conn = get_connection()
    cursor = conn.cursor()

    # Fetch case first
    cursor.execute("""
        SELECT account_id, decision, risk_score, status
        FROM review_cases
        WHERE case_id = %s
    """, (case_id,))

    row = cursor.fetchone()

    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Case not found")

    if row["status"] == "RESOLVED":
        conn.close()
        raise HTTPException(status_code=400, detail="Case already resolved")

    account_id = row["account_id"]

    # Update case
    cursor.execute("""
        UPDATE review_cases
        SET status = 'RESOLVED',
            resolution_type = %s,
            analyst_note = %s,
            resolved_at = %s
        WHERE case_id = %s
    """, (
        req.resolution,
        req.analyst_note,
        datetime.datetime.utcnow(),
        case_id
    ))

    # Audit analyst action (repository layer)
    log_case_resolved(
        cursor,
        account_id=account_id,
        metadata={
            "case_id": case_id,
            "analyst_note": req.analyst_note,
            "resolution": req.resolution,
            "resolution_time": str(datetime.datetime.utcnow()),
        },
    )

    conn.commit()
    conn.close()

    return {
        "message": "Case resolved successfully",
        "case_id": case_id,
        "status": "RESOLVED"
    }
