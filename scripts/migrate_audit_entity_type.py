from app.data.database import get_connection


def migrate():
    conn = get_connection()
    cursor = conn.cursor()

    print("🔧 Running migration: Adding entity_type column...")

    cursor.execute("""
        ALTER TABLE audit_logs
        ADD COLUMN entity_type TEXT DEFAULT 'ACCOUNT';
    """)

    conn.commit()
    conn.close()

    print(" Migration complete: entity_type added successfully.")

if __name__ == "__main__":
    migrate()
