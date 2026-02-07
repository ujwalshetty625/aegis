import uuid
import datetime
from app.data.database import get_connection

def seed_users_and_accounts(n_users=10):
    conn = get_connection()
    cursor = conn.cursor()

    for i in range(n_users):
        user_id = str(uuid.uuid4())
        account_id = str(uuid.uuid4())

        cursor.execute(
            "INSERT INTO users VALUES (?, ?, ?, ?, ?, ?)",
            (
                user_id,
                f"User_{i}",
                f"user{i}@example.com",
                f"+91XXXXXXXX{i}",
                2,
                datetime.datetime.utcnow()
            )
        )

        cursor.execute(
            "INSERT INTO accounts VALUES (?, ?, ?, ?, ?, ?)",
            (
                account_id,
                user_id,
                "wallet",
                10000.0,
                "active",
                datetime.datetime.utcnow()
            )
        )

    conn.commit()
    conn.close()
