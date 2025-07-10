#!/bin/bash
# Render Deployment Script for Restaurant AI Platform
# This script runs on Render during deployment to set up the database and services

set -e  # Exit on any error

echo "🚀 Starting Render deployment..."

# Check if we're running on Render
if [ -z "$RENDER" ]; then
    echo "⚠️  Not running on Render - this script is for Render deployment only"
    exit 1
fi

# Environment validation
echo "🔍 Validating environment variables..."

required_vars=("DATABASE_URL" "REDIS_URL" "OPENAI_API_KEY")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ Required environment variable $var is not set"
        exit 1
    fi
    echo "✅ $var is set"
done

# Install Python dependencies if needed
echo "📦 Installing Python dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    echo "⚠️  No requirements.txt found in root, checking services..."
fi

# Install dependencies for each service
services=("restaurant-service" "menu-service" "ai-service")
for service in "${services[@]}"; do
    if [ -d "backend/$service" ] && [ -f "backend/$service/requirements.txt" ]; then
        echo "📦 Installing dependencies for $service..."
        pip install -r "backend/$service/requirements.txt"
    fi
done

# Test database connectivity
echo "🔗 Testing database connectivity..."
python3 -c "
import psycopg2
import os
import sys

try:
    conn = psycopg2.connect(os.getenv('DATABASE_URL'))
    conn.close()
    print('✅ Database connection successful')
except Exception as e:
    print(f'❌ Database connection failed: {e}')
    sys.exit(1)
"

# Test Redis connectivity
echo "🔗 Testing Redis connectivity..."
python3 -c "
import redis
import os
import sys

try:
    r = redis.from_url(os.getenv('REDIS_URL'))
    r.ping()
    print('✅ Redis connection successful')
except Exception as e:
    print(f'❌ Redis connection failed: {e}')
    sys.exit(1)
"

# Run database migrations
echo "🗄️  Running database migrations..."
python3 scripts/run_migrations.py

# Verify migrations
echo "📊 Checking migration status..."
python3 scripts/run_migrations.py --status

# Create uploads directories if they don't exist
echo "📁 Creating upload directories..."
mkdir -p backend/menu-service/uploads/menu-items
mkdir -p backend/restaurant-service/uploads
chmod 755 backend/menu-service/uploads/menu-items
chmod 755 backend/restaurant-service/uploads

# Seed database with sample data if needed
echo "🌱 Checking if sample data is needed..."
python3 -c "
import psycopg2
import os

conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cursor = conn.cursor()

# Check if we have any restaurants
cursor.execute('SELECT COUNT(*) FROM restaurants')
restaurant_count = cursor.fetchone()[0]

if restaurant_count == 0:
    print('No restaurants found - would seed sample data')
    # Add sample restaurant data here if needed
else:
    print(f'Found {restaurant_count} restaurants - no seeding needed')

conn.close()
"

# Health check for all services
echo "🏥 Running health checks..."

# Test AI service components
echo "🤖 Testing AI service components..."
python3 -c "
import sys
import os
sys.path.append('backend/ai-service')

try:
    from config.ai_config import AIConfigManager
    from services.dynamic_ai_service import DynamicAIService
    
    # Test configuration
    config = AIConfigManager.get_default_config()
    print(f'✅ AI Config: {config.mode.value}')
    
    # Test service creation
    service = DynamicAIService()
    print(f'✅ AI Service: {type(service).__name__}')
    
    print('✅ AI service components working')
except Exception as e:
    print(f'❌ AI service error: {e}')
    sys.exit(1)
"

# Create systemd-style service files for Render (if needed)
echo "⚙️  Service configuration complete"

# Final health check
echo "🏥 Final deployment health check..."
python3 -c "
import os
import psycopg2
import redis

print('🧪 Final Health Check:')

# Database
try:
    conn = psycopg2.connect(os.getenv('DATABASE_URL'))
    cursor = conn.cursor()
    cursor.execute('SELECT version()')
    db_version = cursor.fetchone()[0]
    print(f'✅ Database: Connected ({db_version.split()[0]})')
    conn.close()
except Exception as e:
    print(f'❌ Database: {e}')

# Redis
try:
    r = redis.from_url(os.getenv('REDIS_URL'))
    info = r.info()
    print(f'✅ Redis: Connected (v{info[\"redis_version\"]})')
except Exception as e:
    print(f'❌ Redis: {e}')

# OpenAI API Key
api_key = os.getenv('OPENAI_API_KEY', '')
if api_key and len(api_key) > 20 and not api_key.startswith('sk-fake'):
    print('✅ OpenAI: API key configured')
else:
    print('⚠️  OpenAI: API key not configured (features limited)')

print('✅ Health check complete')
"

echo ""
echo "🎉 Render deployment completed successfully!"
echo ""
echo "🌐 Services deployed:"
echo "   • Restaurant Service: Backend API and restaurant management"
echo "   • Menu Service: Menu items and categories"
echo "   • AI Service: Dynamic AI chat with configuration management"
echo ""
echo "🔧 Features enabled:"
echo "   • Dynamic AI configuration (text-only, speech, hybrid modes)"
echo "   • Restaurant-specific AI settings"
echo "   • Menu image support with fallbacks"
echo "   • Redis caching for performance"
echo "   • Database analytics and audit trails"
echo ""
echo "📊 Next steps:"
echo "   • Monitor application logs"
echo "   • Configure restaurant AI settings via API"
echo "   • Test AI functionality with sample requests"
echo ""
echo "✅ Deployment ready for production traffic!"