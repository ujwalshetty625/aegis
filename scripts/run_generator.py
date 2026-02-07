import sys
import os
import time

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(PROJECT_ROOT)

from app.data.database import init_db, reset_tables
from app.data.seed import seed_users_and_accounts
from app.ingestion.generator import generate_transaction, insert_transaction
from app.signals.engine import generate_spend_signals,generate_velocity_signals,generate_new_device_signals
from app.risk.engine import store_risk_decisions


if __name__ == "__main__":
    # RESET MODE (Option A)
    init_db()
    reset_tables()
    seed_users_and_accounts()

    print("Generating transactions...")

    for _ in range(30):
        txn = generate_transaction()
        insert_transaction(txn)
        time.sleep(0.1)

    print("Computing signals...")
    generate_spend_signals()
    generate_velocity_signals()
    generate_new_device_signals()

    print("Computing risk decisions...")
    store_risk_decisions()

