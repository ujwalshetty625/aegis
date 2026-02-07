import uuid
import datetime
from app.data.database import get_connection

# -------- Signal 1: Total spend in last 24 hours --------

def compute_total_spend_last_24h():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT user_id, SUM(amount)
        FROM transactions
        WHERE txn_timestamp >= datetime('now', '-1 day')
          AND status = 'success'
        GROUP BY user_id
    """)

    rows = cursor.fetchall()
    conn.close()
    return rows


def store_signal(user_id, signal_type, value, description):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO signals VALUES (?, ?, ?, ?, ?, ?)
    """, (
        str(uuid.uuid4()),
        user_id,
        signal_type,
        value,
        description,
        datetime.datetime.utcnow()
    ))

    conn.commit()
    conn.close()


def generate_spend_signals():
    spend_data = compute_total_spend_last_24h()

    for user_id, total_spend in spend_data:
        # Skip users with no spend
        if total_spend is None or total_spend <= 0:
            continue

        store_signal(
            user_id=user_id,
            signal_type="TOTAL_SPEND_24H",
            value=total_spend,
            description=f"User spent ₹{total_spend:.2f} in last 24 hours"
        )
# -------- Signal: Transaction velocity (last 1 hour) --------

def compute_txn_velocity_last_1h():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT user_id, account_id, COUNT(*)
        FROM transactions
        WHERE txn_timestamp >= datetime('now', '-1 hour')
          AND status = 'success'
        GROUP BY user_id, account_id
    """)

    rows = cursor.fetchall()
    conn.close()
    return rows


def generate_velocity_signals(threshold=5):
    velocity_data = compute_txn_velocity_last_1h()

    for user_id, account_id, txn_count in velocity_data:
        if txn_count < threshold:
            continue

        store_signal(
            user_id=user_id,
            signal_type="TXN_VELOCITY_1H",
            value=txn_count,
            description=(
                f"{txn_count} successful transactions in last 1 hour "
                f"for account {account_id}"
            )
        )
# -------- Signal: New device usage --------

def compute_new_device_usage():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT t.user_id, t.account_id, t.device_id
        FROM transactions t
        WHERE t.device_id NOT IN (
            SELECT DISTINCT device_id
            FROM transactions
            WHERE txn_timestamp < datetime('now', '-1 day')
        )
        AND t.status = 'success'
        GROUP BY t.user_id, t.account_id, t.device_id
    """)

    rows = cursor.fetchall()
    conn.close()
    return rows


def generate_new_device_signals():
    device_data = compute_new_device_usage()

    for user_id, account_id, device_id in device_data:
        store_signal(
            user_id=user_id,
            signal_type="NEW_DEVICE_USED",
            value=1,
            description=(
                f"New device {device_id} used for account {account_id}"
            )
        )
