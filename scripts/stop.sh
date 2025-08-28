#!/bin/bash

# Liên Quân Automation API Stop Script
# This script stops the entire system

echo "🛑 Stopping Liên Quân Automation API..."

# Stop all services
docker-compose down

echo "✅ All services stopped"

# Optional: Remove volumes (uncomment if you want to clear data)
# echo "🗑️ Removing volumes..."
# docker-compose down -v

echo ""
echo "📋 To start again: ./scripts/start.sh"
echo "📊 To view logs: docker-compose logs -f"
