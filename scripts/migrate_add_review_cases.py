from app.data.database import get_connection


def migrate():
    conn = get_connection()
    cursor = conn.cursor()

    print("🔧 Adding review_cases table...")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS review_cases (
        case_id TEXT PRIMARY KEY,
        user_id INTEGER NOT NULL,
        account_id INTEGER NOT NULL,
        decision TEXT NOT NULL,
        risk_score REAL NOT NULL,
        status TEXT DEFAULT 'OPEN',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    conn.commit()
    conn.close()

    print(" Migration complete: review_cases table created.")


if __name__ == "__main__":
    migrate()
