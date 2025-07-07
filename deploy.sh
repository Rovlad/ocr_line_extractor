#!/bin/bash

# Deployment script for Piping Line Extractor
set -e

# Configuration
COMPOSE_FILE="docker-compose.yml"
ENV_FILE=".env"
CONTAINER_NAME="piping-line-extractor"

echo "🚀 Deploying Piping Line Extractor"
echo "=================================="
echo ""

# Check if .env file exists
if [ ! -f "$ENV_FILE" ]; then
    echo "❌ Error: .env file not found!"
    echo ""
    echo "Please create a .env file with your Google Cloud credentials:"
    echo "GOOGLE_CLOUD_PROJECT_ID=your-project-id"
    echo "DOCUMENT_AI_PROCESSOR_ID=your-processor-id"
    echo "GOOGLE_APPLICATION_CREDENTIALS_JSON={\"your\":\"service-account-json\"}"
    echo ""
    echo "You can copy from env.example and modify it."
    exit 1
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running!"
    echo "Please start Docker and try again."
    exit 1
fi

# Stop existing containers
echo "🛑 Stopping existing containers..."
docker-compose down --remove-orphans || true
echo ""

# Build and start services
echo "🔨 Building and starting services..."
docker-compose up --build -d

echo ""
echo "⏳ Waiting for services to be ready..."

# Wait for health check
for i in {1..30}; do
    if docker exec $CONTAINER_NAME python -c "import requests; requests.get('http://localhost:8000/health')" 2>/dev/null; then
        echo "✅ Service is healthy and ready!"
        break
    fi
    
    if [ $i -eq 30 ]; then
        echo "❌ Service failed to become healthy within 5 minutes"
        echo "Check logs with: docker-compose logs"
        exit 1
    fi
    
    echo "   Attempt $i/30 - waiting 10 seconds..."
    sleep 10
done

echo ""
echo "🎉 Deployment Complete!"
echo "======================"
echo ""
echo "📍 Service URLs:"
echo "   • API Server: http://localhost:8000"
echo "   • Health Check: http://localhost:8000/health"
echo "   • API Documentation: http://localhost:8000/docs"
echo "   • Test Interface: http://localhost:8000/test_ui.html"
echo ""
echo "📊 Container Status:"
docker-compose ps
echo ""
echo "📝 Useful Commands:"
echo "   • View logs: docker-compose logs -f"
echo "   • Stop services: docker-compose down"
echo "   • Restart: docker-compose restart"
echo "   • Shell access: docker exec -it $CONTAINER_NAME bash"
echo ""

# Show resource usage
echo "💾 Resource Usage:"
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}" $CONTAINER_NAME 