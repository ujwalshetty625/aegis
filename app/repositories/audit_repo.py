from typing import Any, Dict

from app.audit.logger import log_event


def log_transaction_created(
    cursor: Any,
    *,
    account_id: str,
    metadata: Dict,
) -> None:
    """Append a TRANSACTION_CREATED audit event."""
    log_event(
        cursor,
        event_type="TRANSACTION_CREATED",
        entity_type="ACCOUNT",
        entity_id=account_id,
        metadata=metadata,
    )


def log_signals_generated(
    cursor: Any,
    *,
    account_id: str,
    metadata: Dict,
) -> None:
    """Append a SIGNALS_GENERATED audit event."""
    log_event(
        cursor,
        event_type="SIGNALS_GENERATED",
        entity_type="ACCOUNT",
        entity_id=account_id,
        metadata=metadata,
    )


def log_decision_made(
    cursor: Any,
    *,
    account_id: str,
    metadata: Dict,
) -> None:
    """
    Append a DECISION_MADE audit event for an account.
    """
    log_event(
        cursor,
        event_type="DECISION_MADE",
        entity_type="ACCOUNT",
        entity_id=account_id,
        metadata=metadata,
    )


def log_case_opened(
    cursor: Any,
    *,
    account_id: str,
    metadata: Dict,
) -> None:
    """
    Append a CASE_OPENED audit event for an account.
    """
    log_event(
        cursor,
        event_type="CASE_OPENED",
        entity_type="ACCOUNT",
        entity_id=account_id,
        metadata=metadata,
    )


def log_case_resolved(
    cursor: Any,
    *,
    account_id: str,
    metadata: Dict,
) -> None:
    """
    Append a CASE_RESOLVED audit event for an account.
    """
    log_event(
        cursor,
        event_type="CASE_RESOLVED",
        entity_type="ACCOUNT",
        entity_id=account_id,
        metadata=metadata,
    )

