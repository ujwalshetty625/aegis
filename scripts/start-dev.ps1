# Aegis Development Startup
# Run from project root: .\scripts\start-dev.ps1

Write-Host "=== Aegis Dev Environment ===" -ForegroundColor Cyan

# 1. Start Postgres
Write-Host "`n1. Starting PostgreSQL..." -ForegroundColor Yellow
docker start aegis-postgres 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "   Creating and starting postgres container..."
    docker-compose up -d postgres
    Start-Sleep -Seconds 3
}

# 2. Check .env
if (-not (Test-Path .env)) {
    Write-Host "`n2. Copy .env.example to .env" -ForegroundColor Yellow
    Copy-Item .env.example .env
    Write-Host "   Created .env - ensure DATABASE_URL is correct"
} else {
    Write-Host "`n2. .env exists" -ForegroundColor Green
}

# 3. Backend
Write-Host "`n3. Start backend: python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"
Write-Host "   Then in another terminal: cd frontend/aegis-console && npm run dev"
Write-Host "`n   Backend: http://127.0.0.1:8000/docs"
Write-Host "   Frontend: http://localhost:3000"
