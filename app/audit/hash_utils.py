import hashlib
import json


def compute_event_hash(
    prev_hash: str,
    event_type: str,
    entity_type: str,
    entity_id: int,
    metadata: dict
) -> str:
    """
    Compute SHA256 hash for an audit event.

    Hash is based on:
    prev_hash + event_type + entity_type + entity_id + metadata

    This creates tamper-evident audit chaining.
    """

    payload = {
        "prev_hash": prev_hash,
        "event_type": event_type,
        "entity_type": entity_type,
        "entity_id": entity_id,
        "metadata": metadata,
    }

    encoded = json.dumps(payload, sort_keys=True).encode("utf-8")

    return hashlib.sha256(encoded).hexdigest()
