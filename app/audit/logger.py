import json
from app.audit.hash_utils import compute_event_hash


def log_event(cursor, event_type: str, entity_type: str, entity_id, metadata: dict):
    """
    Day 11: Tamper-Evident Audit Logger (FIXED)

    Ensures proper hash chaining by treating entity_id consistently as TEXT.
    """

    entity_id = str(entity_id)  # 🔑 THE ACTUAL FIX

    # 1. Fetch previous hash
    cursor.execute(
        """
        SELECT event_hash
        FROM audit_logs
        WHERE entity_type = %s
          AND entity_id = %s
          AND event_hash IS NOT NULL
        ORDER BY created_at DESC
        LIMIT 1
        """,
        (entity_type, entity_id),
    )


    row = cursor.fetchone()
    prev_hash = row["event_hash"] if row and row["event_hash"] else "GENESIS"

    # 2. Compute hash
    event_hash = compute_event_hash(
        prev_hash=prev_hash,
        event_type=event_type,
        entity_type=entity_type,
        entity_id=entity_id,
        metadata=metadata,
    )

    # 3. Insert chained audit row
    cursor.execute(
        """
        INSERT INTO audit_logs (
            event_type,
            entity_type,
            entity_id,
            metadata,
            prev_hash,
            event_hash
        )
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (
            event_type,
            entity_type,
            entity_id,
            json.dumps(metadata),
            prev_hash,
            event_hash,
        ),
    )
