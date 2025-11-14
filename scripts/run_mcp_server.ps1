# Start MCP Server (PowerShell)

Write-Host "Starting NovaCRM MCP Server..." -ForegroundColor Cyan
Write-Host "MCP Protocol: http://127.0.0.1:3000"
Write-Host "REST API: http://127.0.0.1:3001"
Write-Host "Swagger: http://127.0.0.1:3001/docs"
Write-Host ""

$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location (Join-Path $scriptPath "..")
python servers/mcp_nova/server.py

