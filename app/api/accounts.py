from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
import uuid
import datetime
import pytz

from app.data.database import get_connection

router = APIRouter(prefix="/accounts", tags=["Accounts"])


class CreateAccountRequest(BaseModel):
    name: str
    email: EmailStr
    phone: str


@router.post("/create")
def create_account(req: CreateAccountRequest):
    """
    Create user + create account, returning identifiers.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()

        IST = pytz.timezone("Asia/Kolkata")
        now = datetime.datetime.now(IST)   # ✅ correct

        user_id = str(uuid.uuid4())
        account_id = str(uuid.uuid4())

        cursor.execute(
            """
            INSERT INTO users (user_id, name, email, phone, kyc_level, created_at)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (user_id, req.name, req.email, req.phone, 2, now),
        )

        cursor.execute(
            """
            INSERT INTO accounts (account_id, user_id, account_type, balance, status, created_at)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (account_id, user_id, "wallet", 10000.0, "active", now),
        )

        conn.commit()
        return {"account_id": account_id, "user_id": user_id, "created_at": now}
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


@router.get("")
def list_accounts(limit: int = 200):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT account_id, user_id, status, balance, created_at
            FROM accounts
            ORDER BY created_at DESC
            LIMIT %s
            """,
            (limit,),
        )
        rows = cursor.fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


@router.get("/{account_id}")
def account_details(account_id: str):
    """
    Account details = profile + last decision + open case + last 10 signals.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT account_id, user_id, account_type, balance, status, created_at
            FROM accounts
            WHERE account_id = %s
            LIMIT 1
            """,
            (account_id,),
        )
        acct = cursor.fetchone()
        if not acct:
            raise HTTPException(status_code=404, detail="Account not found")

        user_id = acct["user_id"]

        cursor.execute(
            """
            SELECT decision, risk_score, reasons, created_at
            FROM risk_decisions
            WHERE account_id = %s
            ORDER BY created_at DESC
            LIMIT 1
            """,
            (account_id,),
        )
        latest_decision = cursor.fetchone()

        cursor.execute(
            """
            SELECT case_id, decision, risk_score, status, created_at
            FROM review_cases
            WHERE account_id = %s
              AND status = 'OPEN'
            ORDER BY created_at DESC
            LIMIT 1
            """,
            (account_id,),
        )
        open_case = cursor.fetchone()

        cursor.execute(
            """
            SELECT signal_type, signal_value, signal_weight, signal_contribution, description, created_at
            FROM signals
            WHERE user_id = %s
            ORDER BY created_at DESC
            LIMIT 10
            """,
            (user_id,),
        )
        signals = cursor.fetchall()

        # Aggregate transaction stats for this account
        cursor.execute(
            """
            SELECT
              COUNT(*) AS total_txns
            FROM transactions
            WHERE account_id = %s
            """,
            (account_id,),
        )
        tx_agg = cursor.fetchone() or {"total_txns": 0}

        cursor.execute(
            """
            SELECT txn_id, amount, device_id, txn_timestamp, status
            FROM transactions
            WHERE account_id = %s
            ORDER BY txn_timestamp DESC
            LIMIT 1
            """,
            (account_id,),
        )
        last_txn = cursor.fetchone()

        return {
            "profile": dict(acct),
            "latest_decision": dict(latest_decision) if latest_decision else None,
            "open_case": dict(open_case) if open_case else None,
            "recent_signals": [dict(s) for s in signals],
            "total_transactions": tx_agg["total_txns"],
            "last_transaction": dict(last_txn) if last_txn else None,
        }
    finally:
        conn.close()


@router.get("/{account_id}/transactions")
def account_transactions(account_id: str, limit: int = 50):
    """
    Return last N transactions with decision + risk_score.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT 1
            FROM accounts
            WHERE account_id = %s
            LIMIT 1
            """,
            (account_id,),
        )
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Account not found")

        cursor.execute(
            """
            SELECT
              t.txn_id,
              t.account_id,
              t.amount,
              t.txn_timestamp AS timestamp,
              t.device_id,
              t.channel,
              d.decision,
              d.risk_score
            FROM transactions t
            LEFT JOIN LATERAL (
              SELECT decision, risk_score
              FROM risk_decisions
              WHERE account_id = t.account_id
                AND created_at >= t.txn_timestamp
              ORDER BY created_at ASC
              LIMIT 1
            ) d ON TRUE
            WHERE t.account_id = %s
            ORDER BY t.txn_timestamp DESC
            LIMIT %s
            """,
            (account_id, limit),
        )
        rows = cursor.fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()

