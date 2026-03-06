import os

DATABASE_URL = os.getenv("DATABASE_URL")

BLOCK_THRESHOLD = float(os.getenv("BLOCK_THRESHOLD", 70))
REVIEW_THRESHOLD = float(os.getenv("REVIEW_THRESHOLD", 40))