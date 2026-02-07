import uuid
import datetime
import json


def log_event(cursor, event_type, entity_id, metadata: dict):
    """
    Audit logger using existing DB cursor.
    Prevents SQLite locking issues.
    """

    cursor.execute("""
        INSERT INTO audit_logs
        VALUES (?, ?, ?, ?, ?)
    """, (
        str(uuid.uuid4()),
        event_type,
        entity_id,
        json.dumps(metadata),
        datetime.datetime.utcnow()
    ))
