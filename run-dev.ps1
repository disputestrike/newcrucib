# Run CrucibAI backend + frontend (Windows PowerShell)
# Usage: .\run-dev.ps1

$ErrorActionPreference = "Stop"
$root = $PSScriptRoot

# Start backend in background
$backendDir = Join-Path $root "backend"
Write-Host "Starting backend on http://127.0.0.1:8000 ..." -ForegroundColor Cyan
Start-Process -FilePath "python" -ArgumentList "-m", "uvicorn", "server:app", "--host", "127.0.0.1", "--port", "8000" -WorkingDirectory $backendDir -WindowStyle Normal

Start-Sleep -Seconds 2

# Start frontend (foreground so you see logs)
$frontendDir = Join-Path $root "frontend"
Write-Host "Starting frontend on http://localhost:3000 ..." -ForegroundColor Cyan
Set-Location $frontendDir
& npm start
