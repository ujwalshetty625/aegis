from fastapi import APIRouter, HTTPException
import json

from app.data.database import get_connection
from app.audit.hash_utils import compute_event_hash
from app.core.logging import get_logger


router = APIRouter(prefix="/audit", tags=["Audit Integrity"])

logger = get_logger(__name__)


@router.get("/integrity")
def audit_integrity():
    """
    Verify global audit log hash chain integrity.
    """
    try:
        conn = get_connection()
    except Exception as exc:
        logger.error("Audit integrity: database unreachable: %s", exc)
        raise HTTPException(status_code=503, detail="Database unreachable") from exc

    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT audit_id,
                   event_type,
                   entity_type,
                   entity_id,
                   metadata,
                   prev_hash,
                   event_hash,
                   created_at
            FROM audit_logs
            ORDER BY created_at ASC
            """
        )
        rows = cursor.fetchall()

        total_events = len(rows)
        last_event_time = rows[-1]["created_at"] if rows else None

        audit_chain_valid = True
        for row in rows:
            prev_hash = row["prev_hash"] or "GENESIS"
            raw_metadata = row["metadata"]
            metadata = json.loads(raw_metadata) if raw_metadata else {}

            recomputed = compute_event_hash(
                prev_hash=prev_hash,
                event_type=row["event_type"],
                entity_type=row["entity_type"],
                entity_id=row["entity_id"],
                metadata=metadata,
            )
            if recomputed != row["event_hash"]:
                audit_chain_valid = False
                logger.error(
                    "Audit integrity failed for audit_id=%s", row["audit_id"]
                )
                break

        return {
            "audit_chain_valid": audit_chain_valid,
            "total_events": total_events,
            "last_event_time": last_event_time,
            # frontend contract convenience
            "last_event": last_event_time,
        }
    finally:
        conn.close()

