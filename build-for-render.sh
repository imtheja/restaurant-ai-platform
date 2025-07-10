#!/bin/bash
# Simple, reliable build script for Render deployment

set -e

echo "🚀 Building for Render deployment..."

# Navigate to frontend
cd frontend

echo "📦 Installing dependencies..."
npm ci

echo "🧹 Cleaning previous build..."
rm -rf dist

echo "🔧 Setting environment for production..."
export NODE_ENV=production
export VITE_API_BASE_URL=https://restaurant-ai-backend.onrender.com

echo "🏗️  Building application..."
npx vite build

echo "📁 Verifying build..."
if [ -d "dist" ]; then
    echo "✅ Build successful"
    echo "📊 Build contents:"
    ls -la dist/
    
    # Ensure _redirects exists
    if [ ! -f "dist/_redirects" ]; then
        echo "/*    /index.html   200" > dist/_redirects
        echo "✅ Created _redirects file"
    fi
    
    echo "🔗 Asset references in index.html:"
    grep -o 'assets/[^"]*' dist/index.html || echo "No asset references found"
    
else
    echo "❌ Build failed - no dist directory"
    exit 1
fi

echo "🎉 Build completed successfully!"
echo "Ready for deployment to Render"