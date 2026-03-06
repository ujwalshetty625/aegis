import uuid
import datetime
from typing import Any, Dict


def insert_transaction(
    cursor: Any,
    *,
    account_id: str,
    amount: float,
    device_id: str,
) -> Dict[str, Any]:

    cursor.execute(
        """
        SELECT user_id
        FROM accounts
        WHERE account_id = %s
        """,
        (account_id,),
    )

    row = cursor.fetchone()
    if not row:
        raise ValueError(f"Account not found for account_id={account_id}")

    user_id = row["user_id"]

    txn_id = str(uuid.uuid4())
    now = datetime.datetime.utcnow()

    txn = {
        "txn_id": txn_id,
        "user_id": user_id,
        "account_id": account_id,
        "amount": float(amount),
        "txn_type": "debit",
        "channel": "upi",
        "merchant_category": "generic",
        "location": "Unknown",
        "device_id": device_id,
        "txn_timestamp": now,
        "status": "success",
    }

    cursor.execute(
        """
        INSERT INTO transactions
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (
            txn["txn_id"],
            txn["user_id"],
            txn["account_id"],
            txn["amount"],
            txn["txn_type"],
            txn["channel"],
            txn["merchant_category"],
            txn["location"],
            txn["device_id"],
            txn["txn_timestamp"],
            txn["status"],
        ),
    )

    return txn