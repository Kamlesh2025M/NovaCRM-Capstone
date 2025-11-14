#!/bin/bash

# NovaCRM Assistant Setup Script
# This script sets up the environment and builds the FAISS index

set -e

echo "=================================="
echo "NovaCRM Assistant Setup"
echo "=================================="
echo ""

# Check Python version
echo "Checking Python version..."
python --version || python3 --version

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo ""
    echo "Creating virtual environment..."
    python -m venv venv || python3 -m venv venv
else
    echo ""
    echo "Virtual environment already exists"
fi

# Activate virtual environment
echo "Activating virtual environment..."
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

# Install requirements
echo ""
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Check for .env file
echo ""
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo ""
    echo "WARNING: Please edit .env file and add your OPENAI_API_KEY"
    echo ""
else
    echo ".env file already exists"
fi

# Build FAISS index if not exists
if [ ! -d "index/faiss_index" ]; then
    echo ""
    echo "Building FAISS index for knowledge base..."
    python scripts/build_index.py
else
    echo ""
    echo "FAISS index already exists"
fi

echo ""
echo "=================================="
echo "Setup Complete!"
echo "=================================="
echo ""
echo "Next steps:"
echo "1. Edit .env file and add your OPENAI_API_KEY (if not done)"
echo "2. Start MCP server: python servers/mcp_nova/server.py"
echo "3. Start CLI: python -m app.cli"
echo "   OR"
echo "4. Start API: python -m app.api"
echo ""

