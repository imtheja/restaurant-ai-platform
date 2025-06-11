# Complete Render Deployment Guide for Restaurant AI Platform

This guide provides step-by-step instructions for deploying the full-stack Restaurant AI Platform on Render.

## Deployment Order

Deploy services in this order to ensure dependencies are met:
1. PostgreSQL Database
2. Redis Instance
3. Backend Services (Restaurant, Menu, AI)
4. Frontend Static Site

## 1. PostgreSQL Database

### Steps:
1. Go to your Render Dashboard
2. Click "New +" → "PostgreSQL"
3. Configure:
   - **Name**: `restaurant-ai-db`
   - **Database**: `restaurant_ai_db`
   - **User**: `restaurant_user`
   - **Region**: Choose closest to your users
   - **PostgreSQL Version**: 15
   - **Plan**: Choose based on needs (Free tier available)
4. Click "Create Database"
5. Once created, copy the **Internal Database URL** (starts with `postgres://`)

### Important Values to Save:
- Internal Database URL (for backend services)
- External Database URL (for migrations if needed)

## 2. Redis Instance

### Steps:
1. Click "New +" → "Redis"
2. Configure:
   - **Name**: `restaurant-ai-redis`
   - **Region**: Same as PostgreSQL
   - **Maxmemory Policy**: `allkeys-lru`
   - **Plan**: Choose based on needs
3. Click "Create Redis"
4. Once created, copy the **Internal Redis URL**

### Important Values to Save:
- Internal Redis URL (for backend services)

## 3. Restaurant Service (Backend)

### Steps:
1. Click "New +" → "Web Service"
2. Connect your GitHub repository
3. Configure:
   - **Name**: `restaurant-ai-restaurant-service`
   - **Root Directory**: `backend/restaurant-service`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Free or Starter

### Environment Variables:
Add these in the "Environment" tab:
```
DATABASE_URL=[Internal PostgreSQL URL from step 1]
REDIS_URL=[Internal Redis URL from step 2]
SECRET_KEY=[Generate a secure random string]
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
```

### Advanced Settings:
- **Health Check Path**: `/health` (if implemented)
- **Auto-Deploy**: Yes (for automatic deployments on git push)

4. Click "Create Web Service"

## 4. Menu Service (Backend)

### Steps:
1. Click "New +" → "Web Service"
2. Connect same GitHub repository
3. Configure:
   - **Name**: `restaurant-ai-menu-service`
   - **Root Directory**: `backend/menu-service`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Free or Starter

### Environment Variables:
```
DATABASE_URL=[Internal PostgreSQL URL from step 1]
REDIS_URL=[Internal Redis URL from step 2]
SECRET_KEY=[Same as Restaurant Service]
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
```

4. Click "Create Web Service"

## 5. AI Service (Backend)

### Steps:
1. Click "New +" → "Web Service"
2. Connect same GitHub repository
3. Configure:
   - **Name**: `restaurant-ai-ai-service`
   - **Root Directory**: `backend/ai-service`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Starter or higher (AI services need more resources)

### Environment Variables:
```
DATABASE_URL=[Internal PostgreSQL URL from step 1]
REDIS_URL=[Internal Redis URL from step 2]
OPENAI_API_KEY=[Your OpenAI API key]
SECRET_KEY=[Same as other services]
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
```

4. Click "Create Web Service"

## 6. Frontend (Static Site)

### First, update your frontend API configuration:

Create a file `frontend/.env.production`:
```
VITE_API_BASE_URL=https://restaurant-ai-restaurant-service.onrender.com
VITE_MENU_SERVICE_URL=https://restaurant-ai-menu-service.onrender.com
VITE_AI_SERVICE_URL=https://restaurant-ai-ai-service.onrender.com
```

### Steps:
1. Click "New +" → "Static Site"
2. Connect same GitHub repository
3. Configure:
   - **Name**: `restaurant-ai-frontend`
   - **Root Directory**: `frontend`
   - **Build Command**: `npm install && npm run build`
   - **Publish Directory**: `dist`

### Environment Variables:
```
VITE_API_BASE_URL=https://restaurant-ai-restaurant-service.onrender.com
VITE_MENU_SERVICE_URL=https://restaurant-ai-menu-service.onrender.com
VITE_AI_SERVICE_URL=https://restaurant-ai-ai-service.onrender.com
```

4. Click "Create Static Site"

## 7. Post-Deployment Steps

### Initialize Database:
1. Go to your PostgreSQL dashboard on Render
2. Click "Connect" → "External Connection"
3. Use a PostgreSQL client or Render's shell to run your init.sql:
   ```bash
   psql [EXTERNAL_DATABASE_URL] -f backend/shared/database/init.sql
   ```

### Update CORS Settings:
Ensure your backend services allow requests from your frontend URL. Update each service's CORS configuration to include:
```python
origins = [
    "https://restaurant-ai-frontend.onrender.com",
    "http://localhost:5173",  # for local development
]
```

### Configure Custom Domain (Optional):
1. In your Static Site settings, add custom domain
2. Update DNS records as instructed by Render
3. Update environment variables to use custom domain

## 8. Monitoring and Logs

### For each service:
1. Go to service dashboard
2. Click "Logs" tab to view real-time logs
3. Set up alerts in "Settings" → "Notifications"

## Environment Variables Summary

### All Backend Services Need:
- `DATABASE_URL` - PostgreSQL internal URL
- `REDIS_URL` - Redis internal URL  
- `SECRET_KEY` - Shared secret for JWT/sessions
- `ENVIRONMENT` - Set to "production"
- `DEBUG` - Set to "false"
- `LOG_LEVEL` - Set to "INFO"

### AI Service Additionally Needs:
- `OPENAI_API_KEY` - Your OpenAI API key

### Frontend Needs:
- `VITE_API_BASE_URL` - Restaurant service URL
- `VITE_MENU_SERVICE_URL` - Menu service URL
- `VITE_AI_SERVICE_URL` - AI service URL

## Troubleshooting

### Common Issues:

1. **Build Failures**: 
   - Check build logs for missing dependencies
   - Ensure requirements.txt is up to date
   - Verify Python version compatibility

2. **Connection Errors**:
   - Verify environment variables are set correctly
   - Check service URLs include `https://`
   - Ensure CORS is configured properly

3. **Database Issues**:
   - Verify DATABASE_URL is the internal URL
   - Check if migrations/init.sql ran successfully
   - Look for connection pool exhaustion

4. **Performance Issues**:
   - Upgrade service plans if needed
   - Check for memory/CPU limits
   - Enable caching where appropriate

## Cost Optimization Tips

1. Start with free tiers for testing
2. Use Render's autoscaling for production
3. Set up proper caching to reduce API calls
4. Monitor usage and upgrade only as needed

## Security Checklist

- [ ] All secrets in environment variables
- [ ] HTTPS enabled on all services
- [ ] CORS properly configured
- [ ] Database access restricted to internal network
- [ ] API rate limiting enabled
- [ ] Logging doesn't expose sensitive data