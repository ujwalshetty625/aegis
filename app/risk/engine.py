import uuid
import datetime
import json

from app.data.database import get_connection
from app.audit.logger import log_event


# =========================================================
# SIGNAL WEIGHTS (Deterministic Risk Contributions)
# =========================================================

SIGNAL_WEIGHTS = {
    "TOTAL_SPEND_24H": 0.002,
    "TXN_VELOCITY_1H": 8.0,
    "NEW_DEVICE_USED": 15.0
}

REVIEW_THRESHOLD = 40
BLOCK_THRESHOLD = 70


# =========================================================
# DAY 5 (Legacy) — USER LEVEL SCORING (Not Used Now)
# =========================================================

def fetch_signals():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT user_id,
               description,
               signal_type,
               signal_value
        FROM signals
    """)

    rows = cursor.fetchall()
    conn.close()
    return rows


def compute_risk_scores():
    signals = fetch_signals()
    risk_map = {}

    for user_id, description, signal_type, value in signals:
        weight = SIGNAL_WEIGHTS.get(signal_type, 0)
        contribution = weight * value

        if user_id not in risk_map:
            risk_map[user_id] = {"score": 0, "reasons": []}

        risk_map[user_id]["score"] += contribution
        risk_map[user_id]["reasons"].append(
            f"{signal_type}: {description}"
        )

    return risk_map


def store_risk_decisions():
    """
    Old user-level decisioning (not used after Day 6).
    """
    risk_map = compute_risk_scores()

    conn = get_connection()
    cursor = conn.cursor()

    for user_id, data in risk_map.items():
        score = round(min(data["score"], 100), 2)

        if score >= BLOCK_THRESHOLD:
            decision = "BLOCK"
        elif score >= REVIEW_THRESHOLD:
            decision = "REVIEW"
        else:
            decision = "ALLOW"

        cursor.execute("""
            INSERT INTO risk_decisions
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            str(uuid.uuid4()),
            user_id,
            None,
            score,
            decision,
            " | ".join(data["reasons"]),
            datetime.datetime.utcnow()
        ))

    conn.commit()
    conn.close()


# =========================================================
# DAY 6+7 — ACCOUNT LEVEL SCORING + AUDITABLE DECISIONS
# =========================================================

def fetch_signals_with_accounts():
    """
    Fetch signals joined with accounts through transactions.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT s.user_id,
               t.account_id,
               s.signal_type,
               s.signal_value,
               s.description
        FROM signals s
        JOIN transactions t
          ON s.user_id = t.user_id
        GROUP BY s.signal_id
    """)

    rows = cursor.fetchall()
    conn.close()
    return rows


def compute_account_risk_scores():
    """
    Compute risk scores per (user_id, account_id).
    Store structured reasons with contribution breakdown.
    """
    rows = fetch_signals_with_accounts()
    risk_map = {}

    for user_id, account_id, signal_type, value, description in rows:
        key = (user_id, account_id)

        if key not in risk_map:
            risk_map[key] = {"score": 0, "reasons": []}

        weight = SIGNAL_WEIGHTS.get(signal_type, 0)
        contribution = weight * value

        risk_map[key]["score"] += contribution

        # Store structured reason
        risk_map[key]["reasons"].append({
            "type": signal_type,
            "description": description,
            "contribution": round(contribution, 2)
        })

    return risk_map


def fetch_latest_decision(user_id, account_id):
    """
    Fetch latest decision for deduplication.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT risk_score, decision
        FROM risk_decisions
        WHERE user_id = ? AND account_id = ?
        ORDER BY created_at DESC
        LIMIT 1
    """, (user_id, account_id))

    row = cursor.fetchone()
    conn.close()
    return row


def summarize_reasons(reasons: list):
    """
    Convert raw reason list into analyst-friendly summary.
    """
    summary = {}

    for r in reasons:
        t = r["type"]
        summary[t] = summary.get(t, 0) + 1

    return " | ".join(
        [f"{k}: {v} triggers" for k, v in summary.items()]
    )


def store_account_risk_decisions():
    """
    Store account-level risk decisions with:
    - Deduplication
    - Structured audit logs
    - Clean summarized reasons
    """
    risk_map = compute_account_risk_scores()

    conn = get_connection()
    cursor = conn.cursor()

    for (user_id, account_id), data in risk_map.items():
        raw_score = data["score"]
        score = round(min(raw_score, 100), 2)

        # Threshold decisions
        if score >= BLOCK_THRESHOLD:
            decision = "BLOCK"
        elif score >= REVIEW_THRESHOLD:
            decision = "REVIEW"
        else:
            decision = "ALLOW"

        # Deduplication check
        latest = fetch_latest_decision(user_id, account_id)

        if latest:
            prev_score, prev_decision = latest
            if prev_decision == decision and abs(prev_score - score) < 1:
                continue

        # Summarized reasons for DB readability
        reasons_text = summarize_reasons(data["reasons"])

        # Insert decision
        cursor.execute("""
            INSERT INTO risk_decisions
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            str(uuid.uuid4()),
            user_id,
            account_id,
            score,
            decision,
            reasons_text,
            datetime.datetime.utcnow()
        ))

        # AUDIT LOG (inside loop, correct placement)
        log_event(
    cursor,
    event_type="DECISION_MADE",
    entity_id=account_id,
    metadata={
        "user_id": user_id,
        "account_id": account_id,
        "risk_score": score,
        "decision": decision,
        "reasons": data["reasons"]
    }
)

    conn.commit()
    conn.close()
