from app.data.database import get_connection


def migrate():
    conn = get_connection()
    cursor = conn.cursor()

    print("🔧 Fixing audit_logs entity_id type...")

    # 1. Rename old table
    cursor.execute("ALTER TABLE audit_logs RENAME TO audit_logs_old;")

    # 2. Create new correct table
    cursor.execute("""
    CREATE TABLE audit_logs (
        audit_id TEXT PRIMARY KEY,
        event_type TEXT,
        entity_type TEXT DEFAULT 'ACCOUNT',
        entity_id INTEGER,
        metadata TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        prev_hash TEXT,
        event_hash TEXT
    );
    """)

    # 3. Copy old data
    cursor.execute("""
    INSERT INTO audit_logs (audit_id, event_type, entity_type, entity_id, metadata, created_at)
    SELECT audit_id, event_type, entity_type, CAST(entity_id AS INTEGER), metadata, created_at
    FROM audit_logs_old;
    """)

    conn.commit()
    conn.close()

    print(" Migration complete. entity_id is now INTEGER.")


if __name__ == "__main__":
    migrate()
