#!/bin/bash
# Debug Render deployment issues

echo "🔍 Debugging Render Frontend Deployment Issues"
echo "=============================================="

# Check local build
echo "1. Testing local build..."
cd frontend

if [ ! -f "package.json" ]; then
    echo "❌ Not in frontend directory"
    exit 1
fi

echo "📦 Installing dependencies..."
npm ci

echo "🏗️  Building locally..."
if npm run build; then
    echo "✅ Local build successful"
    
    if [ -d "dist" ]; then
        echo "✅ dist directory created"
        echo "📁 Build contents:"
        ls -la dist/
        
        if [ -f "dist/index.html" ]; then
            echo "✅ index.html exists"
            echo "🔍 Checking asset references in index.html:"
            grep -o 'assets/[^"]*' dist/index.html | head -10
        else
            echo "❌ index.html missing!"
        fi
    else
        echo "❌ dist directory not created!"
    fi
else
    echo "❌ Local build failed!"
    exit 1
fi

cd ..

# Check for common issues
echo ""
echo "2. Checking for common deployment issues..."

# Check build command in package.json
echo "🔍 Frontend package.json build script:"
grep -A 1 '"build"' frontend/package.json

# Check for _redirects file
if [ -f "frontend/public/_redirects" ]; then
    echo "✅ _redirects file exists:"
    cat frontend/public/_redirects
else
    echo "⚠️  _redirects file missing - creating one..."
    echo "/*    /index.html   200" > frontend/public/_redirects
    echo "✅ Created _redirects file"
fi

# Check environment files
echo ""
echo "🔍 Environment configuration:"
if [ -f "frontend/.env.production" ]; then
    echo "✅ .env.production exists:"
    cat frontend/.env.production
else
    echo "❌ .env.production missing!"
fi

echo ""
echo "🔍 Recommended Render Settings:"
echo "================================"
echo "Service Type: Static Site"
echo "Build Command: cd frontend && npm ci && npm run build"
echo "Publish Directory: frontend/dist"
echo "Environment Variables:"
echo "  NODE_ENV=production"
echo "  GENERATE_SOURCEMAP=false"
echo ""
echo "📋 Troubleshooting Steps:"
echo "1. Check Render build logs for errors"
echo "2. Verify the publish directory contains files"
echo "3. Ensure _redirects file is in dist/"
echo "4. Check if assets are being generated with correct paths"