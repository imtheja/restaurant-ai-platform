#!/bin/bash
# Render-specific build script

set -e

echo "🚀 Starting Render build process..."

# Navigate to frontend directory
cd frontend

echo "📦 Installing dependencies..."
npm ci --production=false

echo "🧹 Cleaning previous builds..."
rm -rf dist

echo "🔧 Setting up environment..."
# Copy production env
cp .env.production .env.local

echo "🏗️  Building for production..."
npm run build

echo "📁 Verifying build output..."
if [ -d "dist" ]; then
    echo "✅ Build directory created"
    echo "📊 Build size:"
    du -sh dist
    
    echo "📄 Generated files:"
    ls -la dist/
    
    if [ -f "dist/index.html" ]; then
        echo "✅ index.html generated"
        echo "🔗 Asset references:"
        grep -o 'assets/[^"]*' dist/index.html
    else
        echo "❌ index.html missing!"
        exit 1
    fi
    
    if [ -f "dist/_redirects" ]; then
        echo "✅ _redirects file present"
    else
        echo "⚠️  _redirects file missing"
        echo "/*    /index.html   200" > dist/_redirects
        echo "✅ Created _redirects file"
    fi
else
    echo "❌ Build failed - no dist directory"
    exit 1
fi

echo "🎉 Build completed successfully!"
echo "📂 Static files ready in frontend/dist/"