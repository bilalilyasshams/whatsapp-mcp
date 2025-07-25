#!/bin/bash
set -e

# Start WhatsApp bridge in background
echo "Starting WhatsApp bridge..."
cd /app
./whatsapp-bridge &
BRIDGE_PID=$!

# Wait for bridge to initialize
sleep 5

# Start HTTP MCP server
echo "Starting MCP HTTP server..."
cd /app/whatsapp-mcp-server
exec uv run python http_server.py
