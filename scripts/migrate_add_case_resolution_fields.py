from app.data.database import get_connection


def migrate():
    conn = get_connection()
    cursor = conn.cursor()

    print("🔧 Adding analyst_note + resolved_at columns...")

    cursor.execute("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = 'review_cases'
    """)
    cols = [row["column_name"] for row in cursor.fetchall()]

    if "analyst_note" not in cols:
        cursor.execute("ALTER TABLE review_cases ADD COLUMN analyst_note TEXT;")

    if "resolved_at" not in cols:
        cursor.execute("ALTER TABLE review_cases ADD COLUMN resolved_at TIMESTAMP;")

    conn.commit()
    conn.close()

    print(" Migration complete.")


if __name__ == "__main__":
    migrate()
