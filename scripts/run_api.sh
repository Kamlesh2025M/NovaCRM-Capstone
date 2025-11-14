#!/bin/bash

# Start FastAPI Application

echo "Starting NovaCRM Assistant API..."
echo "API: http://127.0.0.1:8000"
echo "Swagger: http://127.0.0.1:8000/docs"
echo ""
echo "NOTE: MCP server must be running on port 3001"
echo ""

cd "$(dirname "$0")/.."
python -m app.api

