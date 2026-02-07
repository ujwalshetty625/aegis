import sqlite3
from app.data.schema import RISK_DECISIONS_TABLE, USER_TABLE, ACCOUNT_TABLE, TRANSACTION_TABLE, SIGNALS_TABLE

DB_PATH = "data/aegis.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(USER_TABLE)
    cursor.execute(ACCOUNT_TABLE)
    cursor.execute(TRANSACTION_TABLE)
    cursor.execute(SIGNALS_TABLE)
    cursor.execute(RISK_DECISIONS_TABLE)
    

    conn.commit()
    conn.close()

def reset_tables():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM transactions;")
    cursor.execute("DELETE FROM accounts;")
    cursor.execute("DELETE FROM users;")

    conn.commit()
    conn.close()
