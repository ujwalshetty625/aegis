import uuid
import datetime
from app.data.database import get_connection


def backfill():
    conn = get_connection()
    cursor = conn.cursor()

    print("🔧 Backfilling review_cases from existing decisions...")

    cursor.execute("""
        SELECT user_id, account_id, decision, risk_score
       FROM risk_decisions
WHERE decision IN ('REVIEW', 'BLOCK')
  AND account_id IS NOT NULL

    """)

    rows = cursor.fetchall()
    created = 0

    for user_id, account_id, decision, score in rows:
        # Skip if an open case already exists for this account
        cursor.execute("""
            SELECT 1 FROM review_cases
            WHERE account_id = %s AND status = 'OPEN'
        """, (account_id,))

        if cursor.fetchone():
            continue

        cursor.execute("""
            INSERT INTO review_cases (
                case_id,
                user_id,
                account_id,
                decision,
                risk_score,
                status,
                created_at
            )
            VALUES (%s, %s, %s, %s, %s, 'OPEN', %s)
        """, (
            str(uuid.uuid4()),
            user_id,
            account_id,
            decision,
            score,
            datetime.datetime.utcnow()
        ))

        created += 1

    conn.commit()
    conn.close()

    print(f"Backfill complete. Created {created} review cases.")


if __name__ == "__main__":
    backfill()
