import time
from typing import Any, Dict, List, Optional

from app.repositories.signal_repo import insert_signal
from app.core.logging import get_logger
from app.repositories.transaction_repo import insert_transaction
from app.repositories.decision_repo import fetch_latest_decision, insert_decision
from app.repositories.case_repo import create_review_case
from app.repositories.audit_repo import (
    log_transaction_created,
    log_signals_generated,
    log_decision_made,
    log_case_opened,
)
from app.risk.engine import SIGNAL_WEIGHTS, REVIEW_THRESHOLD, BLOCK_THRESHOLD

Session = Any

logger = get_logger(__name__)


class RiskPipeline:
    def __init__(self, db: Session):
        self.db = db

    def process_transaction(
        self,
        account_id: str,
        amount: float,
        device_id: str,
    ) -> Dict[str, Any]:

        started_at = time.monotonic()
        cursor = self.db.cursor()

        # Persist transaction
        txn = insert_transaction(
            cursor,
            account_id=account_id,
            amount=amount,
            device_id=device_id,
        )

        if not txn:
            raise ValueError("Transaction insert failed")

        user_id = txn.get("user_id")

        log_transaction_created(
            cursor,
            account_id=account_id,
            metadata={
                "transaction_id": txn["txn_id"],
                "amount": amount,
                "device_id": device_id,
                "timestamp": str(txn["txn_timestamp"]),
            },
        )

        latest = fetch_latest_decision(cursor, account_id=account_id)

        previous_decision: Optional[str] = None

        if latest:
            _, previous_decision = latest

        # Defensive: signal generation should never crash the pipeline
        try:
            signals = self._generate_signals(cursor, account_id=account_id, txn=txn)
        except Exception:
            logger.exception("Signal generation failed for account_id=%s", account_id)
            signals = []

        risk_score, signal_breakdown = self._compute_risk_score(signals)

        for signal in signals:
            insert_signal(cursor, user_id, signal)

        if signals:
            log_signals_generated(
                cursor,
                account_id=account_id,
                metadata={
                    "signals": signals,
                    "signal_breakdown": signal_breakdown,
                },
            )

        if risk_score >= BLOCK_THRESHOLD:
            decision = "BLOCK"
        elif risk_score >= REVIEW_THRESHOLD:
            decision = "REVIEW"
        else:
            decision = "ALLOW"

        if previous_decision is None:
            decision_transition = "NEW"
        elif previous_decision == decision:
            decision_transition = "NO_CHANGE"
        else:
            decision_transition = f"{previous_decision}->{decision}"

        reasons_text = self._summarize_signals(signals)

        insert_decision(
            cursor,
            user_id=user_id,
            account_id=account_id,
            risk_score=risk_score,
            decision=decision,
            reasons=reasons_text,
        )

        case_created = False

        if decision in ("REVIEW", "BLOCK"):

            case = create_review_case(
                cursor,
                user_id=user_id,
                account_id=account_id,
                decision=decision,
                risk_score=risk_score,
            )

            case_created = True

            log_case_opened(
                cursor,
                account_id=account_id,
                metadata={
                    "case_id": case["case_id"],
                    "decision": decision,
                    "risk_score": risk_score,
                    "status": case["status"],
                },
            )

        log_decision_made(
            cursor,
            account_id=account_id,
            metadata={
                "user_id": user_id,
                "account_id": account_id,
                "transaction_id": txn["txn_id"],
                "risk_score": risk_score,
                "decision": decision,
                "previous_decision": previous_decision,
                "decision_transition": decision_transition,
                "signals": signals,
                "signal_breakdown": signal_breakdown,
            },
        )

        latency_ms = (time.monotonic() - started_at) * 1000.0

        return {
            "transaction_id": txn["txn_id"],
            "risk_score": risk_score,
            "decision": decision,
            "previous_decision": previous_decision,
            "decision_transition": decision_transition,
            "signals": signals,
            "signal_breakdown": signal_breakdown,
            "case_created": case_created,
            "decision_latency_ms": round(latency_ms, 2),
        }

    def _generate_signals(self, cursor: Any, *, account_id: str, txn: Dict[str, Any]):

        signals: List[Dict[str, Any]] = []

        if float(txn.get("amount", 0)) > 5000:
            signals.append(
                {
                    "type": "HIGH_AMOUNT",
                    "value": float(txn["amount"]),
                    "description": f"Transaction amount ₹{float(txn['amount']):.2f} exceeds 5000 threshold",
                }
            )

        cursor.execute(
            """
            SELECT COALESCE(SUM(amount),0) AS total_spend
            FROM transactions
            WHERE account_id=%s
            AND txn_timestamp >= NOW() - INTERVAL '1 day'
            """,
            (account_id,),
        )

        row = cursor.fetchone()

        total_spend = float(row["total_spend"] if row else 0)

        if total_spend > 0:
            signals.append(
                {
                    "type": "TOTAL_SPEND_24H",
                    "value": total_spend,
                    "description": f"Account spent ₹{total_spend:.2f} in last 24 hours",
                }
            )

        return signals

    def _compute_risk_score(self, signals):

        raw_score = 0
        signal_breakdown = []

        for signal in signals:

            signal_type = signal["type"]
            value = float(signal["value"])

            weight = SIGNAL_WEIGHTS.get(signal_type, 0)

            contribution = weight * value

            raw_score += contribution

            signal["weight"] = weight
            signal["contribution"] = round(contribution, 2)

            signal_breakdown.append(
                {
                    "type": signal_type,
                    "value": value,
                    "weight": weight,
                    "contribution": round(contribution, 2),
                }
            )

        risk_score = round(min(max(raw_score, 0), 100), 2)

        return risk_score, signal_breakdown

    def _summarize_signals(self, signals):

        if not signals:
            return "no active signals"

        return " | ".join([f"{s['type']}: {s['description']}" for s in signals])