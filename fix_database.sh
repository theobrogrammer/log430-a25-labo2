#!/bin/bash
# Script pour réinitialiser et corriger la base de données

echo "🔧 Fixing database and container issues..."

# Stop all containers
echo "📦 Stopping containers..."
docker compose down

# Remove all containers, networks, images (clean slate)
echo "🧹 Cleaning up old containers and volumes..."
docker compose down --volumes --remove-orphans
docker system prune -f

# Remove MySQL volume to force recreation
echo "🗑️ Removing MySQL data volume..."
docker volume rm log430-a25-labo2_mysql_data 2>/dev/null || true

# Rebuild and start containers
echo "🏗️ Rebuilding containers..."
docker compose build --no-cache

echo "🚀 Starting containers..."
docker compose up -d

# Wait for services to be ready
echo "⏳ Waiting for MySQL to be ready..."
sleep 30

# Check if MySQL is accessible
echo "🔍 Testing MySQL connection..."
docker compose exec mysql mysql -u labo02 -plabo02 -e "SELECT 'MySQL is working!' as status;"

# Check if Redis is working
echo "🔍 Testing Redis connection..."
docker compose exec redis redis-cli ping

# Test the web application
echo "🌐 Testing web application..."
sleep 5
curl -f http://localhost:5000 && echo "✅ Web app is responding" || echo "❌ Web app not responding"

# Run tests
echo "🧪 Running tests..."
docker compose exec store_manager bash -c "cd /app/src && PYTHONPATH=. python -m pytest tests/ -v"

echo "✅ Setup complete!"