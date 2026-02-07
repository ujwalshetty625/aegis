import uuid
import random
import datetime
from app.data.database import get_connection

MERCHANT_CATEGORIES = [
    "food", "groceries", "fuel", "travel",
    "shopping", "entertainment", "utilities"
]

CHANNELS = ["upi", "card", "bank_transfer"]
LOCATIONS = ["Bangalore", "Mumbai", "Delhi", "Chennai", "Hyderabad"]


def fetch_users_and_accounts():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT u.user_id, a.account_id
        FROM users u
        JOIN accounts a ON u.user_id = a.user_id
        WHERE a.status = 'active'
    """)

    rows = cursor.fetchall()
    conn.close()
    return rows


def generate_transaction():
    users = fetch_users_and_accounts()
    user_id, account_id = random.choice(users)

    txn = {
        "txn_id": str(uuid.uuid4()),
        "user_id": user_id,
        "account_id": account_id,
        "amount": round(random.uniform(10, 5000), 2),
        "txn_type": "debit",
        "channel": random.choice(CHANNELS),
        "merchant_category": random.choice(MERCHANT_CATEGORIES),
        "location": random.choice(LOCATIONS),
        "device_id": f"device_{random.randint(1, 20)}",
        "txn_timestamp": datetime.datetime.utcnow(),
        "status": random.choices(
            ["success", "failed"],
            weights=[0.95, 0.05]
        )[0]
    }

    return txn


def insert_transaction(txn):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO transactions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
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
        txn["status"]
    ))

    conn.commit()
    conn.close()
