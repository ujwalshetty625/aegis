import uuid
import datetime
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
from app.core.logging import get_logger


logger = get_logger(__name__)


def initialize_database():
    """
    Idempotent schema initialization + minimal seeding.
    """
    try:
        conn = get_connection()
    except Exception as exc:
        logger.error("Failed to connect to database during startup: %s", exc)
        raise

    try:
        cursor = conn.cursor()

        # Create tables (idempotent)
        cursor.execute(USER_TABLE)
        cursor.execute(ACCOUNT_TABLE)
        cursor.execute(TRANSACTION_TABLE)
        cursor.execute(SIGNALS_TABLE)
        cursor.execute(RISK_DECISIONS_TABLE)
        cursor.execute(AUDIT_LOG_TABLE)
        cursor.execute(REVIEW_CASES_TABLE)

        # Schema drift hardening (idempotent Postgres-only)
        cursor.execute("ALTER TABLE signals ADD COLUMN IF NOT EXISTS signal_weight REAL;")
        cursor.execute("ALTER TABLE signals ADD COLUMN IF NOT EXISTS signal_contribution REAL;")
        cursor.execute("ALTER TABLE signals ADD COLUMN IF NOT EXISTS description TEXT;")
        cursor.execute("ALTER TABLE audit_logs ADD COLUMN IF NOT EXISTS prev_hash TEXT;")
        cursor.execute("ALTER TABLE audit_logs ADD COLUMN IF NOT EXISTS event_hash TEXT;")
        cursor.execute("ALTER TABLE audit_logs ADD COLUMN IF NOT EXISTS created_at TIMESTAMP;")
        cursor.execute("ALTER TABLE review_cases ADD COLUMN IF NOT EXISTS resolution_type TEXT;")
        cursor.execute("ALTER TABLE review_cases ADD COLUMN IF NOT EXISTS analyst_note TEXT;")
        cursor.execute("ALTER TABLE review_cases ADD COLUMN IF NOT EXISTS resolved_at TIMESTAMP;")

        # Performance indexes (idempotent)
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_transactions_account_id ON transactions(account_id);"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_transactions_timestamp ON transactions(txn_timestamp);"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_risk_decisions_account_id ON risk_decisions(account_id);"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON audit_logs(created_at);"
        )

        # Seed minimal users + accounts if empty
        cursor.execute("SELECT COUNT(*) as count FROM users;")
        result = cursor.fetchone()
        if result and result["count"] == 0:
            seed_minimal_data(cursor)

        conn.commit()
        logger.info("Database schema initialized and minimal data ensured.")
    except Exception as exc:
        conn.rollback()
        logger.error("Database initialization failed: %s", exc)
        raise
    finally:
        conn.close()


def seed_minimal_data(cursor):
    now = datetime.datetime.utcnow()

    user_id = str(uuid.uuid4())
    account_id = str(uuid.uuid4())

    cursor.execute(
        """
        INSERT INTO users (user_id, name, email, phone, kyc_level, created_at)
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (user_id, "Demo User", "demo@aegis.com", "9999999999", 2, now),
    )

    cursor.execute(
        """
        INSERT INTO accounts (account_id, user_id, account_type, balance, status, created_at)
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (account_id, user_id, "savings", 10000.0, "active", now),
    )