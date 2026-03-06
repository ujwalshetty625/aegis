from fastapi import APIRouter
import json

from app.data.database import get_connection
from app.core.logging import get_logger
from app.audit.hash_utils import compute_event_hash
from app.services.pipeline import RiskPipeline


router = APIRouter(prefix="/system", tags=["System"])

logger = get_logger(__name__)


@router.get("/health/deep")
def deep_health():
    """
    Extended health check with database + audit chain validation.
    """
    health = {
        "ok": True,
        "database": False,
        "database_status": False,
        "tables": {},
        "tables_status": {},
        "audit_chain_valid": True,
        "total_audit_events": 0,
        "last_audit_timestamp": None,
    }

    try:
        conn = get_connection()
    except Exception as exc:
        logger.error("Deep health: database unreachable: %s", exc)
        health["ok"] = False
        health["database"] = False
        health["database_status"] = False
        return health

    try:
        cursor = conn.cursor()
        health["database"] = True
        health["database_status"] = True

        # Basic table presence checks
        required_tables = [
            "users",
            "accounts",
            "transactions",
            "signals",
            "risk_decisions",
            "audit_logs",
            "review_cases",
        ]
        cursor.execute(
            """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            """
        )
        existing = {row["table_name"] for row in cursor.fetchall()}
        for t in required_tables:
            health["tables"][t] = t in existing
            health["tables_status"][t] = t in existing

        # Audit chain verification
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
        health["total_audit_events"] = len(rows)
        if rows:
            health["last_audit_timestamp"] = rows[-1]["created_at"]

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
                    "Audit chain mismatch for audit_id=%s", row["audit_id"]
                )
                break

        health["audit_chain_valid"] = audit_chain_valid
        if not audit_chain_valid:
            health["ok"] = False

        return health
    finally:
        conn.close()


@router.post("/test-transaction")
def test_transaction():
    """
    Generate and evaluate a synthetic transaction for a random active account.
    """
    try:
        conn = get_connection()
    except Exception as exc:
        logger.error("Test transaction: database unreachable: %s", exc)
        from fastapi import HTTPException
        raise HTTPException(status_code=503, detail="Database unreachable") from exc

    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT account_id
            FROM accounts
            WHERE status = 'active'
            ORDER BY created_at ASC
            LIMIT 1
            """
        )
        row = cursor.fetchone()
        if not row:
            from fastapi import HTTPException
            raise HTTPException(status_code=400, detail="No active accounts available")

        account_id = row["account_id"]

        # Simple deterministic test payload
        amount = 100.0
        device_id = "test_device_system"

        pipeline = RiskPipeline(conn)
        result = pipeline.process_transaction(
            account_id=account_id,
            amount=amount,
            device_id=device_id,
        )
        conn.commit()

        logger.info(
            "Test transaction processed for account_id=%s decision=%s score=%.2f",
            account_id,
            result.get("decision"),
            result.get("risk_score", 0.0),
        )

        return result
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

