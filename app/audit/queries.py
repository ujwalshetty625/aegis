import json


def fetch_account_audit(cursor, account_id: int, *, limit: int, offset: int):
    """
    Fetch paginated audit history for a given account_id.

    Filters only ACCOUNT-level events for regulator-grade traceability:
    - SIGNAL_GENERATED events
    - DECISION_MADE events
    """

    cursor.execute(
        """
        SELECT
            audit_id,
            event_type,
            entity_type,
            entity_id,
            metadata,
            created_at
        FROM audit_logs
        WHERE entity_type = 'ACCOUNT' AND entity_id = %s
        ORDER BY created_at ASC
        LIMIT %s OFFSET %s
        """,
        (str(account_id), limit, offset),
    )

    rows = cursor.fetchall()

    audit_events = []
    for row in rows:
        audit_events.append(
            {
                "audit_id": row["audit_id"],
                "event_type": row["event_type"],
                "entity_type": row["entity_type"],
                "entity_id": row["entity_id"],
                "metadata": json.loads(row["metadata"]) if row["metadata"] else {},
                "created_at": row["created_at"],
            }
        )

    return audit_events
