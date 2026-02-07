import uuid
import datetime
import json
from app.data.database import get_connection


def log_event(event_type, entity_id, metadata: dict):
    """
    Immutable audit log entry.
    Stores structured metadata for traceability.
    """
    conn = get_connection()
    cursor = conn.cursor()

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

    conn.commit()
    conn.close()
