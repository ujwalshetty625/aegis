# Aegis — Adaptive Explainable FinTech Risk & Intelligence Platform

Aegis is a backend risk intelligence system inspired by real-world fraud and risk engines used inside digital payments platforms and NBFC lending infrastructure.

This project focuses on building the core components that production fintech companies rely on internally:

- continuous transaction ingestion  
- behavioral risk signal generation  
- account-level scoring and decisioning  
- explainability and auditability  
- API-first service design  

Aegis is not a toy ML notebook or a CRUD demo.  
It is being developed as an industry-shaped risk decisioning backend.

---

## Problem Context

Modern fintech platforms need to continuously answer:

- Is this account behaving abnormally?
- Should this activity be allowed, reviewed, or blocked?
- Can we justify the decision to auditors and compliance teams?
- Can the system evolve from rules into ML-driven intelligence?

Aegis is built around these constraints from day one.

---

## Implemented Features

### 1. Transaction Ingestion + Financial Data Model

Aegis generates realistic transaction streams and stores them in a structured schema:

- users  
- accounts  
- transactions  

SQLite is used initially for rapid iteration (Postgres migration planned).

---

### 2. Behavioral Signal Engine

Before introducing ML, Aegis builds the signal layer used in real fraud systems.

Current signals:

- `TOTAL_SPEND_24H` — spend intensity anomaly  
- `TXN_VELOCITY_1H` — burst transaction detection  
- `NEW_DEVICE_USED` — device trust and behavioral drift  

Signals are stored and queryable in the database.

---

### 3. Account-Level Risk Scoring and Decisions

Risk is computed per `(user_id, account_id)` rather than only per user.

Decisions produced:

- `ALLOW`
- `REVIEW`
- `BLOCK`

Scoring is deterministic and transparent, designed to be extensible into ML later.

---

### 4. Explainability by Design

Every risk decision includes explicit reasoning derived from triggered signals.

Example:

TOTAL_SPEND_24H: 1 trigger | TXN_VELOCITY_1H: 1 trigger | NEW_DEVICE_USED: 4 triggers

This mirrors how fraud analysts interpret risk outputs in production.

---

### 5. Immutable Audit Logging (Compliance Foundation)

Aegis maintains an append-only audit trail for:

- signal generation events  
- decision events  

Audit metadata is stored as structured JSON.

Audit writes occur in the same database transaction as decisions to ensure atomicity and prevent orphan records.

---

### 6. FastAPI Service Layer

Aegis is exposed as a running backend service via FastAPI.

Core endpoints:

- `GET /health`
- `GET /signals/recent`
- `GET /decisions/latest`
- `GET /accounts/{account_id}/decision`

Swagger UI:
http://127.0.0.1:8000/docs

## Architecture Overview

Transaction Generator
↓
Database (SQLite → Postgres)
↓
Signal Engine
↓
Account-Level Risk Engine
↓
Explainability + Audit Logs
↓
FastAPI Risk Intelligence Service
↓
(Planned) Analyst Dashboard + ML Models

---

## Project Structure

```bash
aegis/
├── app/
│   ├── data/          # schema + DB initialization
│   ├── ingestion/     # transaction generator
│   ├── signals/       # behavioral signal engine
│   ├── risk/          # scoring + decision engine
│   ├── audit/         # immutable audit logging
│   ├── api/           # FastAPI routes
│   └── main.py        # API entrypoint
│
├── scripts/
│   └── run_generator.py
│
├── data/
│   └── aegis.db
└── README.md
