# Aegis — Real-Time Fraud Detection & Risk Intelligence Platform

Aegis is a **real-time fraud detection and risk intelligence platform** designed to monitor financial transactions, generate behavioral risk signals, compute risk scores, and assist analysts in investigating suspicious activity.

The system processes incoming transactions through a **risk pipeline**, evaluates behavioral signals, and automatically classifies transactions into **ALLOW**, **REVIEW**, or **BLOCK** decisions.

Suspicious transactions automatically create **investigation cases**, enabling fraud analysts to inspect transaction activity, understand risk reasoning, and take action.

This project simulates the architecture used by modern fintech fraud detection systems such as **Stripe Radar, PayPal Risk Engine, and Razorpay Fraud Monitoring**.

---

# Live Demo

### Frontend Dashboard
https://aegis-udz4.vercel.app

### Backend API Documentation
https://aegis-api-27xy.onrender.com/docs

---

# System Overview

Aegis simulates a **financial transaction monitoring system** composed of:

1. Transaction ingestion and processing
2. Risk signal generation
3. Risk scoring engine
4. Automated decision system
5. Fraud investigation dashboard

Incoming transactions are evaluated using behavioral signals that contribute to a **weighted risk score**. Based on this score, the system determines whether the transaction should be allowed, reviewed, or blocked.

---

# Core Features

## Account Management
- Create and manage customer accounts
- Track account balances and account status
- Monitor account activity history

## Transaction Processing
- Real-time transaction ingestion
- Transaction simulator for testing scenarios
- Transaction storage and history tracking

## Risk Detection Engine

The system generates behavioral risk signals such as:

- High transaction amount
- Excessive spending within time windows
- Rapid transaction velocity
- High transaction frequency
- New device usage detection

Each signal contributes to the final **risk score**.

---

# Risk Decisions

Transactions are classified into three decision categories:

| Decision | Description |
|--------|-------------|
| **ALLOW** | Transaction considered safe |
| **REVIEW** | Suspicious activity requiring analyst review |
| **BLOCK** | High risk activity detected |

---

# Fraud Investigation Dashboard

The analyst dashboard allows investigation of accounts with detailed insights including:

- Account summary
- Recent transactions
- Generated risk signals
- Latest risk decision
- Active investigation cases

---

# Case Management

Suspicious transactions automatically generate **review cases**.

Fraud analysts can:

- Investigate suspicious activity
- Review signal explanations
- Approve or escalate cases
- Track investigation status

---

# Explainable Risk Scoring

Each transaction decision includes a **transparent breakdown of risk signals**, showing:

- Signal type
- Signal weight
- Contribution to the final risk score

This allows analysts to understand **why a transaction was flagged**.

---

# Audit Integrity System

All important system events are recorded in a **tamper-evident audit log chain**, providing:

- Traceable event history
- Integrity verification
- Forensic investigation support

---

# System Architecture

```
Frontend (Next.js)
        ↓
FastAPI Backend (Risk Engine)
        ↓
Risk Pipeline & Signal Processing
        ↓
PostgreSQL Database
```

---

# Tech Stack

## Frontend
- Next.js
- TypeScript
- TailwindCSS
- Vercel Deployment

## Backend
- FastAPI
- Python
- Uvicorn

## Database
- PostgreSQL
- Neon Cloud Database

## Infrastructure
- Vercel (Frontend Hosting)
- Render (Backend Hosting)

---

# Risk Pipeline Workflow

1. Transaction is received through the ingestion endpoint
2. Transaction is stored in the database
3. Risk signals are generated based on behavioral patterns
4. Signals contribute to a weighted risk score
5. Decision engine classifies the transaction
6. Suspicious transactions generate investigation cases
7. Analysts investigate cases through the dashboard

---

# Example Risk Signals

| Signal | Description |
|------|-------------|
| **HIGH_AMOUNT** | Transaction amount exceeds threshold |
| **TOTAL_SPEND_24H** | Excessive spending within 24 hours |
| **TXN_VELOCITY_1H** | Multiple transactions in short time period |
| **RAPID_TRANSACTIONS** | High frequency transactions in minutes |
| **NEW_DEVICE_USED** | Transaction from previously unseen device |

---

# API Endpoints

### Accounts
- Create accounts
- Fetch account details
- Account investigation data

### Transactions
- Ingest new transactions
- Retrieve transaction history
- Explain transaction decisions

### Risk & Cases
- Latest risk decisions
- Open investigation cases
- Case resolution

### System Monitoring
- Health checks
- Audit chain verification

Full API documentation available at:

https://aegis-api-27xy.onrender.com/docs

---

# Example Use Case

A transaction is injected into the system.

The risk engine analyzes the transaction and detects signals such as:

- High transaction amount
- New device usage
- Rapid transaction frequency

These signals increase the risk score, triggering a **REVIEW decision** and automatically generating an investigation case for analysts.

---

# Project Status

This project represents a **functional prototype of a real-time fraud monitoring system** demonstrating:

- Transaction monitoring
- Behavioral fraud detection
- Automated risk scoring
- Fraud investigation workflows

---

# Author

**Ujwal Shetty**

---

# Future Improvements

Potential future improvements include:

- Machine learning based risk scoring
- Role based authentication
- Real payment gateway integration
- Event streaming architecture
- Graph based fraud detection

---

# License

This project is intended for **educational and demonstration purposes**.
