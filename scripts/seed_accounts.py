import sys
import os
import uuid
import datetime

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(PROJECT_ROOT)

from app.data.database import get_connection  # noqa: E402
from app.core.logging import get_logger  # noqa: E402


logger = get_logger("scripts.seed_accounts")


def main():
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Only seed if there are no users yet
        cursor.execute("SELECT COUNT(*) AS count FROM users;")
        row = cursor.fetchone()
        if row and row["count"] > 0:
            logger.info("Users already present; skipping seed_accounts.")
            conn.close()
            return

        now = datetime.datetime.utcnow()

        users = []
        for i in range(5):
            user_id = str(uuid.uuid4())
            users.append(user_id)
            cursor.execute(
                """
                INSERT INTO users (user_id, name, email, phone, kyc_level, created_at)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    user_id,
                    f"Seed User {i+1}",
                    f"seed{i+1}@aegis.local",
                    f"900000000{i}",
                    2,
                    now,
                ),
            )

        # 10 accounts, 2 per user
        account_types = ["wallet", "savings"]
        for idx, user_id in enumerate(users):
            for t in account_types:
                account_id = str(uuid.uuid4())
                cursor.execute(
                    """
                    INSERT INTO accounts (
                        account_id, user_id, account_type, balance, status, created_at
                    )
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (
                        account_id,
                        user_id,
                        t,
                        10000.0,
                        "active",
                        now,
                    ),
                )

        conn.commit()
        logger.info("Seeded 5 users and 10 accounts.")
    except Exception as exc:
        conn.rollback()
        logger.error("seed_accounts failed: %s", exc)
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()

