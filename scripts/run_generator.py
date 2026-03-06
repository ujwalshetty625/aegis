import sys
import os
import time

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(PROJECT_ROOT)

from app.data.database import get_connection
from app.data.schema import (
    USER_TABLE,
    ACCOUNT_TABLE,
    TRANSACTION_TABLE,
    SIGNALS_TABLE,
    RISK_DECISIONS_TABLE,
    AUDIT_LOG_TABLE,
    REVIEW_CASES_TABLE,
)
from app.data.seed import seed_users_and_accounts
from app.core.logging import get_logger


if __name__ == "__main__":
    """
    Clean boot initializer.

    After refactor, this script is responsible only for:
    - Creating database tables
    - Resetting any existing user/account data
    - Seeding a minimal set of users + accounts

    It intentionally does NOT:
    - Insert transactions
    - Generate signals
    - Compute or insert risk decisions
    - Create review cases
    - Write audit logs
    """

    logger = get_logger("scripts.run_generator")

    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Create tables if not existing
        cursor.execute(USER_TABLE)
        cursor.execute(ACCOUNT_TABLE)
        cursor.execute(TRANSACTION_TABLE)
        cursor.execute(SIGNALS_TABLE)
        cursor.execute(RISK_DECISIONS_TABLE)
        cursor.execute(AUDIT_LOG_TABLE)
        cursor.execute(REVIEW_CASES_TABLE)

        # Truncate core entities
        cursor.execute("DELETE FROM transactions;")
        cursor.execute("DELETE FROM accounts;")
        cursor.execute("DELETE FROM users;")

        conn.commit()

        seed_users_and_accounts()
        logger.info(
            "Database initialized with fresh users and accounts. No transactions or risk data have been generated."
        )
    except Exception as exc:
        conn.rollback()
        logger.error("Run generator script failed: %s", exc)
        raise
    finally:
        conn.close()


