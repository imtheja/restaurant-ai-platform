#!/bin/bash
# Development startup script for Restaurant AI Platform

set -e

echo "🚀 Starting Restaurant AI Platform (Development Mode)"

# Function to check if a port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        echo "⚠️  Port $1 is already in use"
        return 1
    fi
    return 0
}

# Function to wait for service to be ready
wait_for_service() {
    local url=$1
    local service_name=$2
    local max_attempts=30
    local attempt=1

    echo "⏳ Waiting for $service_name to be ready..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s "$url" > /dev/null 2>&1; then
            echo "✅ $service_name is ready!"
            return 0
        fi
        
        echo "Attempt $attempt/$max_attempts: $service_name not ready yet..."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    echo "❌ $service_name failed to start within expected time"
    return 1
}

# Check required ports
echo "🔍 Checking required ports..."
required_ports=(3000 8000 8001 8002 8003 5432 6379)
for port in "${required_ports[@]}"; do
    if ! check_port $port; then
        echo "Please stop the service using port $port and try again"
        exit 1
    fi
done

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p logs uploads

# Load environment variables
if [ -f .env ]; then
    echo "📝 Loading environment variables from .env..."
    export $(cat .env | grep -v '^#' | xargs)
else
    echo "⚠️  No .env file found. Using default environment variables."
fi

# Start infrastructure services
echo "🐳 Starting infrastructure services (PostgreSQL, Redis)..."
docker-compose up -d postgres redis

# Wait for infrastructure services - check if containers are healthy
echo "⏳ Waiting for database containers to be healthy..."
sleep 5

# Check PostgreSQL
echo "Checking PostgreSQL connection..."
docker-compose exec -T postgres pg_isready -U restaurant_user -d restaurant_ai_db || {
    echo "❌ PostgreSQL is not ready. Checking logs..."
    docker-compose logs postgres
    exit 1
}
echo "✅ PostgreSQL is ready!"

# Check Redis
echo "Checking Redis connection..."
docker-compose exec -T redis redis-cli ping || {
    echo "❌ Redis is not ready. Checking logs..."
    docker-compose logs redis
    exit 1
}
echo "✅ Redis is ready!"

# Initialize database
echo "🗄️  Initializing database..."
cd backend
python3 ../scripts/init_db.py
cd ..

# Start backend services in the background
echo "🔧 Starting backend services..."

# Restaurant Service
echo "Starting Restaurant Service..."
cd backend/restaurant-service
echo "Installing dependencies for Restaurant Service..."
pip3 install -q -r requirements.txt
python3 -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload > ../../logs/restaurant-service.log 2>&1 &
RESTAURANT_PID=$!
cd ../..

# Menu Service
echo "Starting Menu Service..."
cd backend/menu-service
echo "Installing dependencies for Menu Service..."
pip3 install -q -r requirements.txt
python3 -m uvicorn main:app --host 0.0.0.0 --port 8002 --reload > ../../logs/menu-service.log 2>&1 &
MENU_PID=$!
cd ../..

# AI Service
echo "Starting AI Service..."
cd backend/ai-service
echo "Installing dependencies for AI Service..."
pip3 install -q -r requirements.txt
python3 -m uvicorn main:app --host 0.0.0.0 --port 8003 --reload > ../../logs/ai-service.log 2>&1 &
AI_PID=$!
cd ../..

# Start Nginx
echo "🌐 Starting API Gateway (Nginx)..."
docker-compose up -d nginx

# Wait for backend services
wait_for_service "http://localhost:8001/health" "Restaurant Service" || exit 1
wait_for_service "http://localhost:8002/health" "Menu Service" || exit 1
wait_for_service "http://localhost:8003/health" "AI Service" || exit 1
wait_for_service "http://localhost:8000/health" "API Gateway" || exit 1

# Start frontend
echo "⚛️  Starting Frontend..."
cd frontend
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install
fi
npm run dev > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

# Wait for frontend
wait_for_service "http://localhost:3000" "Frontend" || exit 1

# Create PID file for cleanup
echo "$RESTAURANT_PID $MENU_PID $AI_PID $FRONTEND_PID" > .dev_pids

echo ""
echo "🎉 Restaurant AI Platform is ready!"
echo ""
echo "🌐 Available services:"
echo "   • Frontend:          http://localhost:3000"
echo "   • API Gateway:       http://localhost:8000"
echo "   • Restaurant API:    http://localhost:8001/docs"
echo "   • Menu API:          http://localhost:8002/docs"
echo "   • AI API:            http://localhost:8003/docs"
echo ""
echo "📝 Sample restaurant: http://localhost:3000/r/marios-italian"
echo ""
echo "🛑 To stop all services, run: ./scripts/stop_dev.sh"
echo ""
echo "📊 Logs are available in the logs/ directory"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down services..."
    
    if [ -f .dev_pids ]; then
        read -r restaurant_pid menu_pid ai_pid frontend_pid < .dev_pids
        
        [ ! -z "$restaurant_pid" ] && kill $restaurant_pid 2>/dev/null || true
        [ ! -z "$menu_pid" ] && kill $menu_pid 2>/dev/null || true
        [ ! -z "$ai_pid" ] && kill $ai_pid 2>/dev/null || true
        [ ! -z "$frontend_pid" ] && kill $frontend_pid 2>/dev/null || true
        
        rm -f .dev_pids
    fi
    
    docker-compose down
    echo "✅ All services stopped"
    exit 0
}

# Register cleanup function
trap cleanup SIGINT SIGTERM

# Keep script running
echo "Press Ctrl+C to stop all services..."
wait
