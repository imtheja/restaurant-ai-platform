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
