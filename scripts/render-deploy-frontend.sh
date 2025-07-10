#!/bin/bash
# Deploy frontend to Render

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }

log_info "🚀 Preparing frontend for Render deployment..."

# Check if we're in the right directory
if [ ! -f "frontend/package.json" ]; then
    log_error "frontend/package.json not found. Please run this script from the project root."
    exit 1
fi

# Step 1: Update environment variables for production
log_info "🔧 Setting up production environment variables..."

# Create/update frontend .env for production
cat > frontend/.env.production << EOF
# Production API URLs for Render
REACT_APP_API_BASE_URL=https://restaurant-ai-backend.onrender.com
REACT_APP_RESTAURANT_API_URL=https://restaurant-ai-backend.onrender.com/api/v1
REACT_APP_MENU_API_URL=https://restaurant-ai-backend.onrender.com/api/v1
REACT_APP_AI_API_URL=https://restaurant-ai-backend.onrender.com/api/v1

# Environment
NODE_ENV=production
GENERATE_SOURCEMAP=false
EOF

log_success "Created frontend/.env.production"

# Step 2: Create Render-specific build command
log_info "📝 Creating Render build configuration..."

# Create render.yaml for automated deployments (optional)
cat > render.yaml << 'EOF'
services:
  # Frontend Static Site
  - type: web
    name: restaurant-ai-frontend
    env: static
    buildCommand: cd frontend && npm ci && npm run build
    staticPublishPath: ./frontend/dist
    routes:
      - type: rewrite
        source: /*
        destination: /index.html
    envVars:
      - key: NODE_ENV
        value: production
      - key: GENERATE_SOURCEMAP
        value: false

  # Backend Service
  - type: web
    name: restaurant-ai-backend
    env: docker
    dockerfilePath: ./Dockerfile
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: restaurant-ai-db
          property: connectionString
      - key: OPENAI_API_KEY
        sync: false  # Set manually in Render dashboard
      - key: NODE_ENV
        value: production

databases:
  - name: restaurant-ai-db
    databaseName: restaurant_ai_db
    user: restaurant_user
EOF

log_success "Created render.yaml"

# Step 3: Update package.json build scripts if needed
log_info "🔧 Checking frontend build configuration..."

cd frontend

# Check if build script exists
if ! grep -q '"build"' package.json; then
    log_warning "Build script not found in package.json"
    # You might need to add it manually
fi

# Step 4: Test build locally
log_info "🏗️  Testing production build locally..."

if npm run build; then
    log_success "Local production build successful!"
    
    # Check if dist directory was created
    if [ -d "dist" ]; then
        log_success "Build output created in frontend/dist/"
        log_info "Build size: $(du -sh dist 2>/dev/null | cut -f1)"
    else
        log_warning "Build output directory not found"
    fi
else
    log_error "Local build failed! Please fix build errors before deploying."
    exit 1
fi

cd ..

# Step 5: Create deployment instructions
log_info "📋 Creating deployment instructions..."

cat > RENDER_DEPLOYMENT.md << 'EOF'
# Render Deployment Instructions

## Frontend Deployment

### Method 1: Connect GitHub Repository (Recommended)

1. **Go to Render Dashboard**: https://dashboard.render.com
2. **Create New Static Site**:
   - Click "New +" → "Static Site"
   - Connect your GitHub repository
   - Select the repository: `restaurant-ai-platform`

3. **Configure Build Settings**:
   - **Build Command**: `cd frontend && npm ci && npm run build`
   - **Publish Directory**: `frontend/dist`
   - **Auto-Deploy**: Yes (deploys on git push)

4. **Environment Variables**:
   ```
   NODE_ENV=production
   GENERATE_SOURCEMAP=false
   ```

5. **Custom Domain** (Optional):
   - Add custom domain in Render dashboard
   - Update DNS records as instructed

### Method 2: Manual Upload

1. **Build locally**:
   ```bash
   cd frontend
   npm run build
   ```

2. **Upload dist folder** to Render static site

## Backend Deployment

### Prerequisites
- Database already deployed: ✅
- Data imported: ✅

### Steps

1. **Create Web Service**:
   - Click "New +" → "Web Service"
   - Connect repository
   - Select `restaurant-ai-platform`

2. **Configure Service**:
   - **Environment**: Docker
   - **Dockerfile Path**: `./Dockerfile` (create if needed)
   - **Build Command**: `docker build -t restaurant-ai-backend .`
   - **Start Command**: `docker run -p $PORT restaurant-ai-backend`

3. **Environment Variables**:
   ```
   DATABASE_URL=[Connect to your PostgreSQL database]
   OPENAI_API_KEY=[Your OpenAI API key]
   NODE_ENV=production
   PORT=$PORT
   ```

## URL Structure

After deployment:
- **Frontend**: https://restaurant-ai-frontend.onrender.com
- **Backend**: https://restaurant-ai-backend.onrender.com
- **Database**: Internal connection

## Testing Deployment

1. **Check frontend loads**: Visit the frontend URL
2. **Check API connectivity**: Frontend should connect to backend
3. **Test restaurant page**: Visit `/r/chip-cookies`
4. **Test AI chat**: Verify chat functionality works

## Troubleshooting

### Frontend Issues
- **404 on routes**: Ensure redirect rules are set for SPA
- **API errors**: Check CORS settings and backend URL
- **Build failures**: Check Node.js version and dependencies

### Backend Issues
- **Database connection**: Verify DATABASE_URL is correct
- **CORS errors**: Ensure frontend domain is allowed
- **API errors**: Check logs in Render dashboard

## Post-Deployment

1. **Update environment variables** if needed
2. **Set up monitoring** in Render dashboard
3. **Configure alerts** for service failures
4. **Set up custom domains** if required

## Notes

- Render automatically builds and deploys on git push
- Free tier has limitations (check Render pricing)
- Database backups are handled by Render PostgreSQL
- SSL certificates are automatic with Render
EOF

log_success "Created RENDER_DEPLOYMENT.md with detailed instructions"

# Final instructions
echo ""
log_success "🎉 Frontend is ready for Render deployment!"
echo ""
log_info "📋 Next Steps:"
echo "  1. Commit and push changes:"
echo "     git add ."
echo "     git commit -m 'Prepare frontend for Render deployment'"
echo "     git push origin main"
echo ""
echo "  2. Go to Render Dashboard: https://dashboard.render.com"
echo "  3. Create a new Static Site"
echo "  4. Connect your GitHub repository"
echo "  5. Use these settings:"
echo "     • Build Command: cd frontend && npm ci && npm run build"
echo "     • Publish Directory: frontend/dist"
echo ""
echo "  6. Read RENDER_DEPLOYMENT.md for detailed instructions"
echo ""
log_warning "⚠️  Don't forget to deploy the backend services too!"
echo "  Your frontend will need the backend APIs to work properly."