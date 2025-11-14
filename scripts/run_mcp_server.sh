#!/bin/bash

# Start MCP Server

echo "Starting NovaCRM MCP Server..."
echo "MCP Protocol: http://127.0.0.1:3000"
echo "REST API: http://127.0.0.1:3001"
echo "Swagger: http://127.0.0.1:3001/docs"
echo ""

cd "$(dirname "$0")/.."
python servers/mcp_nova/server.py

