USER_TABLE = """
CREATE TABLE IF NOT EXISTS users (
    user_id TEXT PRIMARY KEY,
    name TEXT,
    email TEXT,
    phone TEXT,
    kyc_level INTEGER,
    created_at TIMESTAMP
);
"""

ACCOUNT_TABLE = """
CREATE TABLE IF NOT EXISTS accounts (
    account_id TEXT PRIMARY KEY,
    user_id TEXT,
    account_type TEXT,
    balance REAL,
    status TEXT,
    created_at TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(user_id)
);
"""

TRANSACTION_TABLE = """
CREATE TABLE IF NOT EXISTS transactions (
    txn_id TEXT PRIMARY KEY,
    user_id TEXT,
    account_id TEXT,
    amount REAL,
    txn_type TEXT,
    channel TEXT,
    merchant_category TEXT,
    location TEXT,
    device_id TEXT,
    txn_timestamp TIMESTAMP,
    status TEXT,
    FOREIGN KEY(user_id) REFERENCES users(user_id),
    FOREIGN KEY(account_id) REFERENCES accounts(account_id)
);
"""
SIGNALS_TABLE = """
CREATE TABLE IF NOT EXISTS signals (
    signal_id TEXT PRIMARY KEY,
    user_id TEXT,
    signal_type TEXT,
    signal_value REAL,
    description TEXT,
    created_at TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(user_id)
);
"""
RISK_DECISIONS_TABLE = """
CREATE TABLE IF NOT EXISTS risk_decisions (
    decision_id TEXT PRIMARY KEY,
    user_id TEXT,
    account_id TEXT,
    risk_score REAL,
    decision TEXT,
    reasons TEXT,
    created_at TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(user_id),
    FOREIGN KEY(account_id) REFERENCES accounts(account_id)
);
"""
