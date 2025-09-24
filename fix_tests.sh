#!/bin/bash
# Script pour corriger les problèmes de tests et configuration

echo "🔧 Fixing test configuration issues..."

# 1. Vérifier que a.env existe
if [ -f "a.env" ]; then
    echo "✅ a.env file exists and will be used"
    cat a.env
else
    echo "📄 Creating a.env file with default values..."
    cat > a.env << EOF
# MySQL
DB_HOST=mysql
DB_PORT=3306
DB_NAME=labo02_db
DB_USER=labo02
DB_PASS=labo02

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0
EOF
    echo "✅ a.env file created with default values"
fi

# 2. Vérifier la connexion MySQL depuis le conteneur
echo "🔍 Testing MySQL connection from store_manager container..."
docker compose exec store_manager bash -c "mysql -h mysql -u labo02 -plabo02 -e 'SELECT COUNT(*) as user_count FROM users;' labo02_db"

# 3. Vérifier les variables d'environnement dans le conteneur
echo "🔍 Checking environment variables in container..."
docker compose exec store_manager bash -c "cd /app/src && python -c \"
import config
print('DB_HOST:', config.DB_HOST)
print('DB_USER:', config.DB_USER)
print('DB_NAME:', config.DB_NAME)
\""

# 4. Exécuter les tests avec debug
echo "🧪 Running tests with debugging..."
docker compose exec store_manager bash -c "cd /app && ls -la a.env"

# 5. Exécuter les tests
echo "🧪 Running tests..."
docker compose exec store_manager bash -c "cd /app/src && PYTHONPATH=. python -m pytest tests/ -v -s"

echo "✅ Test debugging complete!"