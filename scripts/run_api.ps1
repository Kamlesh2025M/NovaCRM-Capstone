# Start FastAPI Application (PowerShell)

Write-Host "Starting NovaCRM Assistant API..." -ForegroundColor Cyan
Write-Host "API: http://127.0.0.1:8000"
Write-Host "Swagger: http://127.0.0.1:8000/docs"
Write-Host ""
Write-Host "NOTE: MCP server must be running on port 3001" -ForegroundColor Yellow
Write-Host ""

$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location (Join-Path $scriptPath "..")
python -m app.api

