@echo off
REM Script pour réinitialiser et corriger la base de données (Windows)

echo 🔧 Fixing database and container issues...

REM Stop all containers
echo 📦 Stopping containers...
docker compose down

REM Remove all containers, networks, volumes (clean slate)  
echo 🧹 Cleaning up old containers and volumes...
docker compose down --volumes --remove-orphans
docker system prune -f

REM Remove MySQL volume to force recreation
echo 🗑️ Removing MySQL data volume...
docker volume rm log430-a25-labo2_mysql_data 2>nul

REM Rebuild and start containers
echo 🏗️ Rebuilding containers...
docker compose build --no-cache

echo 🚀 Starting containers...
docker compose up -d

REM Wait for services to be ready
echo ⏳ Waiting for MySQL to be ready...
timeout /t 30 /nobreak > nul

REM Check if MySQL is accessible
echo 🔍 Testing MySQL connection...
docker compose exec mysql mysql -u labo02 -plabo02 -e "SELECT 'MySQL is working!' as status;"

REM Check if Redis is working
echo 🔍 Testing Redis connection...
docker compose exec redis redis-cli ping

echo ✅ Setup complete! Try accessing http://localhost:5000
pause