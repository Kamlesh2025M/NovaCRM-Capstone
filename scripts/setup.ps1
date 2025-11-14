# NovaCRM Assistant Setup Script (PowerShell)
# This script sets up the environment and builds the FAISS index

Write-Host "==================================" -ForegroundColor Cyan
Write-Host "NovaCRM Assistant Setup" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# Check Python version
Write-Host "Checking Python version..." -ForegroundColor Yellow
python --version

# Create virtual environment if it doesn't exist
if (-not (Test-Path venv)) {
    Write-Host ""
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
} else {
    Write-Host ""
    Write-Host "Virtual environment already exists" -ForegroundColor Green
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
.\venv\Scripts\Activate.ps1

# Install requirements
Write-Host ""
Write-Host "Installing dependencies..." -ForegroundColor Yellow
python -m pip install --upgrade pip
pip install -r requirements.txt

# Check for .env file
Write-Host ""
if (-not (Test-Path .env)) {
    Write-Host "Creating .env file from template..." -ForegroundColor Yellow
    Copy-Item .env.example .env
    Write-Host ""
    Write-Host "WARNING: Please edit .env file and add your OPENAI_API_KEY" -ForegroundColor Red
    Write-Host ""
} else {
    Write-Host ".env file already exists" -ForegroundColor Green
}

# Build FAISS index if not exists
if (-not (Test-Path "index\faiss_index")) {
    Write-Host ""
    Write-Host "Building FAISS index for knowledge base..." -ForegroundColor Yellow
    python scripts/build_index.py
} else {
    Write-Host ""
    Write-Host "FAISS index already exists" -ForegroundColor Green
}

Write-Host ""
Write-Host "==================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Edit .env file and add your OPENAI_API_KEY (if not done)"
Write-Host "2. Start MCP server: python servers/mcp_nova/server.py"
Write-Host "3. Start CLI: python -m app.cli"
Write-Host "   OR"
Write-Host "4. Start API: python -m app.api"
Write-Host ""

