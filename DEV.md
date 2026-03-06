# Aegis Development Environment

## Prerequisites

- Python 3.13
- Node.js 18+
- Docker (for PostgreSQL)

## Quick Start

### 1. Environment setup

```powershell
# Copy env files
Copy-Item .env.example .env
Copy-Item frontend\aegis-console\.env.local.example frontend\aegis-console\.env.local

# Backend dependencies
pip install -r requirements.txt

# Frontend dependencies (from project root)
cd frontend\aegis-console
npm install
cd ..\..
```

### 2. Start PostgreSQL

```powershell
# Create and start (first time)
docker-compose up -d postgres

# Or if container exists
docker start aegis-postgres
```

Wait a few seconds for Postgres to be ready.

### 3. Start backend

```powershell
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

- API docs: http://127.0.0.1:8000/docs
- Health: http://127.0.0.1:8000/health

### 4. Start frontend

```powershell
cd frontend\aegis-console
npm run dev
```

- App: http://localhost:3000

## Environment Variables

| Variable | Location | Default |
|----------|----------|---------|
| DATABASE_URL | `.env` (root) | postgresql://postgres:password@localhost:5432/aegis |
| NEXT_PUBLIC_API_BASE_URL | `frontend/aegis-console/.env.local` | http://127.0.0.1:8000 |

## Troubleshooting

- **Backend can't connect**: Ensure Postgres is running and DATABASE_URL is correct.
- **Frontend can't reach API**: Check NEXT_PUBLIC_API_BASE_URL and CORS (backend allows localhost:3000).
- **Port in use**: Change port with `--port 8001` (backend) or `next dev -p 3001` (frontend).
- **node_modules issues**: Delete `node_modules` and `package-lock.json` in frontend/aegis-console, run `npm install`.
- **Next.js lock / port conflict**: Kill stale Next.js: `taskkill /F /IM node.exe` (Windows). Or delete `frontend/aegis-console/.next/dev/lock` if orphaned.
