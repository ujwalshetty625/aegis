import uuid
import datetime
from typing import Dict


def insert_signal(cursor, user_id: str, signal: Dict):
    """
    Persist a single computed signal for a user.
    """
    signal_id = str(uuid.uuid4())
    now = datetime.datetime.utcnow()

    cursor.execute(
        """
        INSERT INTO signals (
            signal_id,
            user_id,
            signal_type,
            signal_value,
            signal_weight,
            signal_contribution,
            description,
            created_at
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (
            signal_id,
            user_id,
            signal["type"],
            signal["value"],
            signal.get("weight", 0.0),
            signal.get("contribution", 0.0),
            signal.get("description", ""),
            now,
        ),
    )