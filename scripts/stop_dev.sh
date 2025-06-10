#!/bin/bash
# Stop development services for Restaurant AI Platform

echo "🛑 Stopping Restaurant AI Platform..."

# Kill background processes
if [ -f .dev_pids ]; then
    echo "Stopping backend services..."
    read -r restaurant_pid menu_pid ai_pid frontend_pid < .dev_pids
    
    [ ! -z "$restaurant_pid" ] && kill $restaurant_pid 2>/dev/null && echo "  ✅ Restaurant Service stopped"
    [ ! -z "$menu_pid" ] && kill $menu_pid 2>/dev/null && echo "  ✅ Menu Service stopped"
    [ ! -z "$ai_pid" ] && kill $ai_pid 2>/dev/null && echo "  ✅ AI Service stopped"
    [ ! -z "$frontend_pid" ] && kill $frontend_pid 2>/dev/null && echo "  ✅ Frontend stopped"
    
    rm -f .dev_pids
else
    echo "No PID file found, attempting to kill by port..."
    
    # Kill processes by port
    lsof -ti:8001 | xargs kill 2>/dev/null || true
    lsof -ti:8002 | xargs kill 2>/dev/null || true  
    lsof -ti:8003 | xargs kill 2>/dev/null || true
    lsof -ti:3000 | xargs kill 2>/dev/null || true
    
    echo "  ✅ Killed processes on ports 8001, 8002, 8003, 3000"
fi

# Stop Docker services
echo "Stopping Docker services..."
docker-compose down

echo "✅ All services stopped successfully!"
echo ""
echo "📊 Logs are preserved in the logs/ directory"