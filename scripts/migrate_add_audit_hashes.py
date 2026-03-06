from app.data.database import get_connection


def migrate():
    conn = get_connection()
    cursor = conn.cursor()

    print("🔧 Adding audit hash columns...")

    cursor.execute("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = 'audit_logs'
    """)
    cols = [row["column_name"] for row in cursor.fetchall()]

    if "prev_hash" not in cols:
        cursor.execute("""
            ALTER TABLE audit_logs
            ADD COLUMN prev_hash TEXT;
        """)

    if "event_hash" not in cols:
        cursor.execute("""
            ALTER TABLE audit_logs
            ADD COLUMN event_hash TEXT;
        """)

    conn.commit()
    conn.close()

    print(" Migration complete: prev_hash + event_hash added.")


if __name__ == "__main__":
    migrate()
