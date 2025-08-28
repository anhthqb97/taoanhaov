#!/bin/bash

# Liên Quân Automation API Startup Script
# This script starts the entire system with Docker Compose

set -e

echo "🚀 Starting Liên Quân Automation API..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install it first."
    exit 1
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p screenshots uploads logs mysql/init

# Set permissions
chmod 755 screenshots uploads logs

# Build and start services
echo "🔨 Building and starting services..."
docker-compose up -d --build

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 30

# Check service health
echo "🏥 Checking service health..."

# Check MySQL
if docker-compose exec -T mysql mysqladmin ping -h localhost > /dev/null 2>&1; then
    echo "✅ MySQL is healthy"
else
    echo "❌ MySQL is not healthy"
fi

# Check Redis
if docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; then
    echo "✅ Redis is healthy"
else
    echo "❌ Redis is not healthy"
fi

# Check App
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ FastAPI app is healthy"
else
    echo "❌ FastAPI app is not healthy"
fi

echo ""
echo "🎉 All services are running!"
echo ""
echo "📋 Service URLs:"
echo "  • API Documentation: http://localhost:8000/docs"
echo "  • API Health Check: http://localhost:8000/health"
echo "  • Adminer (Database): http://localhost:8080"
echo "  • Nginx: http://localhost:80"
echo ""
echo "🔐 Default Admin Credentials:"
echo "  • Username: admin"
echo "  • Password: admin123456"
echo ""
echo "📊 To view logs: docker-compose logs -f"
echo "🛑 To stop: docker-compose down"
echo "🔄 To restart: docker-compose restart"
