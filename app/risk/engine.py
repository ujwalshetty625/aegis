import uuid
import datetime
from app.data.database import get_connection
from app.audit.logger import log_event


# -----------------------------
# Signal weights (deterministic)
# -----------------------------
SIGNAL_WEIGHTS = {
    "TOTAL_SPEND_24H": 0.002,      # ₹ → score contribution
    "TXN_VELOCITY_1H": 8.0,        # per txn burst
    "NEW_DEVICE_USED": 15.0        # high-risk behavior
}

# Score thresholds
REVIEW_THRESHOLD = 40
BLOCK_THRESHOLD = 70

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
            risk_map[user_id] = {
                "score": 0,
                "reasons": []
            }

        risk_map[user_id]["score"] += contribution
        risk_map[user_id]["reasons"].append(
            f"{signal_type}: {description}"
        )

    return risk_map

def store_risk_decisions():
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
            None,  # account-level scoring comes later
            score,
            decision,
            " | ".join(data["reasons"]),
            datetime.datetime.utcnow()
        ))

    conn.commit()
    conn.close()




# =========================================================
# DAY 6 — ACCOUNT-LEVEL RISK ENGINE + DEDUPLICATION
# =========================================================

def fetch_signals_with_accounts():
    """
    Fetch signals and associate them with account_ids.
    For now, we join via transactions.
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
    """
    rows = fetch_signals_with_accounts()

    risk_map = {}

    for user_id, account_id, signal_type, value, description in rows:
        key = (user_id, account_id)

        if key not in risk_map:
            risk_map[key] = {
                "score": 0,
                "reasons": []
            }

        weight = SIGNAL_WEIGHTS.get(signal_type, 0)
        contribution = weight * value

        risk_map[key]["score"] += contribution
        risk_map[key]["reasons"].append(
            f"{signal_type}: {description}"
        )

    return risk_map


def fetch_latest_decision(user_id, account_id):
    """
    Fetch the latest stored decision for deduplication.
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


def store_account_risk_decisions():
    """
    Store risk decisions per account with deduplication.
    """
    risk_map = compute_account_risk_scores()

    conn = get_connection()
    cursor = conn.cursor()

    for (user_id, account_id), data in risk_map.items():
        raw_score = data["score"]
        score = round(min(raw_score, 100), 2)

        # Decision thresholds
        if score >= BLOCK_THRESHOLD:
            decision = "BLOCK"
        elif score >= REVIEW_THRESHOLD:
            decision = "REVIEW"
        else:
            decision = "ALLOW"

        # Deduplication: skip if no meaningful change
        latest = fetch_latest_decision(user_id, account_id)

        if latest:
            prev_score, prev_decision = latest

            if prev_decision == decision and abs(prev_score - score) < 1:
                continue

        cursor.execute("""
            INSERT INTO risk_decisions
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            str(uuid.uuid4()),
            user_id,
            account_id,
            score,
            decision,
            " | ".join(data["reasons"]),
            datetime.datetime.utcnow()
        ))

    conn.commit()
    conn.close()
    log_event(
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

