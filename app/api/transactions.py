from fastapi import APIRouter, HTTPException
import json
import traceback
from pydantic import BaseModel

from app.data.database import get_connection
from app.services.pipeline import RiskPipeline
from app.core.logging import get_logger


router = APIRouter(prefix="/transactions", tags=["Transactions"])

logger = get_logger(__name__)


class TransactionRequest(BaseModel):
    account_id: str
    amount: float
    device_id: str


@router.post("")
def ingest_transaction(payload: TransactionRequest):
    """
    Real-time transaction ingestion endpoint.
    """
    conn = get_connection()

    try:
        cursor = conn.cursor()

        # -----------------------------
        # Basic payload validation
        # -----------------------------
        if payload.amount <= 0:
            raise HTTPException(
                status_code=400,
                detail="Amount must be positive",
            )

        if not payload.device_id or not payload.device_id.strip():
            raise HTTPException(
                status_code=400,
                detail="device_id cannot be empty",
            )

        # Validate account exists first
        cursor.execute(
            """
            SELECT account_id, balance
            FROM accounts
            WHERE account_id = %s
            LIMIT 1
            """,
            (payload.account_id,),
        )

        account = cursor.fetchone()

        if not account:
            raise HTTPException(
                status_code=400,
                detail=f"Account not found for account_id={payload.account_id}",
            )

        # Guardrail: prevent overdraft before entering pipeline
        current_balance = float(account.get("balance") or 0.0)
        if payload.amount > current_balance:
            raise HTTPException(
                status_code=400,
                detail="Insufficient balance",
            )

        pipeline = RiskPipeline(conn)

        result = pipeline.process_transaction(
            account_id=payload.account_id,
            amount=payload.amount,
            device_id=payload.device_id,
        )

        # Balance management based on decision outcome
        decision = result.get("decision")
        txn_id = result.get("transaction_id")

        if decision == "ALLOW":
            # Deduct balance only for allowed transactions
            cursor.execute(
                """
                UPDATE accounts
                SET balance = balance - %s
                WHERE account_id = %s
                """,
                (payload.amount, payload.account_id),
            )

        # Persist transaction status aligned with decision
        if txn_id and decision:
            status_value = "success" if decision == "ALLOW" else decision.lower()
            cursor.execute(
                """
                UPDATE transactions
                SET status = %s
                WHERE txn_id = %s
                """,
                (status_value, txn_id),
            )

        conn.commit()

        logger.info(
            "Transaction ingested account_id=%s amount=%.2f decision=%s score=%.2f",
            payload.account_id,
            payload.amount,
            result.get("decision"),
            result.get("risk_score", 0.0),
        )

        return result

    except HTTPException:
        conn.rollback()
        raise

    except Exception as e:
        conn.rollback()

        logger.error("Transaction processing failed")
        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )

    finally:
        conn.close()


@router.get("/{txn_id}/explain")
def explain_transaction(txn_id: str):
    """
    Explainable risk view for a transaction.
    """
    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT txn_id, account_id
            FROM transactions
            WHERE txn_id = %s
            LIMIT 1
            """,
            (txn_id,),
        )

        txn = cursor.fetchone()

        if not txn:
            raise HTTPException(status_code=404, detail="Transaction not found")

        cursor.execute(
            """
            SELECT metadata
            FROM audit_logs
            WHERE event_type = 'DECISION_MADE'
            AND (metadata::jsonb ->> 'transaction_id') = %s
            ORDER BY created_at DESC
            LIMIT 1
            """,
            (txn_id,),
        )

        row = cursor.fetchone()

        if not row:
            raise HTTPException(
                status_code=404,
                detail="No explanation found for transaction",
            )

        metadata = json.loads(row["metadata"]) if row["metadata"] else {}

        decision = metadata.get("decision")
        risk_score = metadata.get("risk_score")

        raw_signals = metadata.get("signals") or []
        breakdown = metadata.get("signal_breakdown") or []

        desc_by_type = {}
        for s in raw_signals:
            if isinstance(s, dict) and "type" in s:
                desc_by_type[s["type"]] = s.get("description")

        signals_out = []

        for s in breakdown:
            if not isinstance(s, dict):
                continue

            t = s.get("type")

            signals_out.append(
                {
                    "type": t,
                    "value": s.get("value"),
                    "weight": s.get("weight"),
                    "contribution": s.get("contribution"),
                    "description": desc_by_type.get(t),
                }
            )

        return {
            "txn_id": txn_id,
            "risk_score": risk_score,
            "decision": decision,
            "signals": signals_out,
        }

    finally:
        conn.close()