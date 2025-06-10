# Restaurant AI Platform - Deployment Guide

## 🚀 Quick Start (Development)

### Prerequisites
- Docker & Docker Compose
- Python 3.11+
- Node.js 18+
- Git

### 1. Clone and Setup
```bash
git clone <repository-url>
cd restaurant-ai-platform
cp .env.example .env
# Edit .env with your configuration
```

### 2. Start Development Environment
```bash
# Make scripts executable
chmod +x scripts/*.sh

# Start all services
./scripts/start_dev.sh
```

### 3. Access the Application
- **Frontend**: http://localhost:3000
- **API Gateway**: http://localhost:8000
- **Sample Restaurant**: http://localhost:3000/r/marios-italian

### 4. Stop Development Environment
```bash
./scripts/stop_dev.sh
```

---

## 🏭 Production Deployment

### Environment Setup

1. **Create production environment file**:
```bash
cp .env.example .env.production
```

2. **Configure environment variables**:
```bash
# Database
DATABASE_URL=postgresql://user:password@postgres:5432/restaurant_ai_db
POSTGRES_USER=restaurant_user
POSTGRES_PASSWORD=secure_production_password
POSTGRES_DB=restaurant_ai_db

# Redis
REDIS_URL=redis://redis:6379/0

# AI Service
OPENAI_API_KEY=your_production_openai_key

# Security
SECRET_KEY=your_super_secure_jwt_key_change_in_production
ALGORITHM=HS256

# Frontend
REACT_APP_API_BASE_URL=https://yourdomain.com

# Domain
DOMAIN=yourdomain.com

# Monitoring (optional)
GRAFANA_PASSWORD=secure_grafana_password
```

### Production Deployment Options

#### Option 1: Docker Compose (Single Server)

```bash
# Build and start production services
docker-compose -f docker-compose.prod.yml up -d

# Check service health
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f
```

#### Option 2: Kubernetes (Recommended for Scale)

```bash
# Apply Kubernetes manifests
kubectl apply -f infrastructure/k8s/

# Check deployment status
kubectl get pods -l app=restaurant-ai

# Get service URLs
kubectl get services
```

#### Option 3: Cloud Deployment

**AWS ECS**:
```bash
# Build and push images
aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin <account>.dkr.ecr.us-west-2.amazonaws.com

# Deploy using CDK/CloudFormation
cd infrastructure/aws
cdk deploy
```

**Google Cloud Run**:
```bash
# Build and deploy
gcloud builds submit --config cloudbuild.yaml
gcloud run deploy restaurant-ai --region us-central1
```

---

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DATABASE_URL` | PostgreSQL connection string | - | ✅ |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379/0` | ✅ |
| `OPENAI_API_KEY` | OpenAI API key for AI features | - | ✅ |
| `SECRET_KEY` | JWT signing key | - | ✅ |
| `CORS_ORIGINS` | Allowed CORS origins | `http://localhost:3000` | ❌ |
| `RATE_LIMIT_PER_MINUTE` | API rate limit | `100` | ❌ |
| `MAX_FILE_SIZE_MB` | Max upload size | `10` | ❌ |

### Database Configuration

The application uses PostgreSQL with the following key features:
- **Connection pooling** for optimal performance
- **Automatic migrations** on startup
- **Sample data** for development
- **Health checks** for monitoring

### Redis Configuration

Redis is used for:
- **Session management**
- **Rate limiting**
- **Menu caching**
- **Real-time features** (Phase 2)

---

## 🔍 Monitoring & Observability

### Health Checks

All services expose health check endpoints:
- `GET /health` - Service health status
- `GET /metrics` - Basic metrics (requests, errors, etc.)

### Logging

Structured logging is implemented across all services:
- **Request/Response logging**
- **Error tracking**
- **Performance metrics**
- **Security events**

### Monitoring Stack (Optional)

Enable monitoring with:
```bash
docker-compose -f docker-compose.prod.yml --profile monitoring up -d
```

This includes:
- **Prometheus** (metrics collection): http://localhost:9090
- **Grafana** (dashboards): http://localhost:3001

---

## 🛡️ Security

### Production Security Checklist

- [ ] Change all default passwords
- [ ] Use strong JWT secret keys
- [ ] Enable HTTPS with valid SSL certificates
- [ ] Configure firewall rules
- [ ] Set up rate limiting
- [ ] Enable monitoring and alerting
- [ ] Regular security updates
- [ ] Database encryption at rest
- [ ] API key rotation policy

### SSL/TLS Setup

1. **Obtain SSL certificates**:
```bash
# Using Let's Encrypt
certbot certonly --webroot -w /var/www/html -d yourdomain.com
```

2. **Configure Nginx**:
```bash
# Copy certificates
cp /etc/letsencrypt/live/yourdomain.com/* infrastructure/ssl/

# Update nginx configuration
# Edit infrastructure/nginx/prod.conf
```

---

## 📊 Scaling

### Horizontal Scaling

The application is designed for horizontal scaling:

```bash
# Scale specific services
docker-compose -f docker-compose.prod.yml up -d --scale restaurant-service=3
docker-compose -f docker-compose.prod.yml up -d --scale ai-service=2
```

### Load Balancing

Nginx is configured with:
- **Round-robin load balancing**
- **Health checks**
- **Automatic failover**
- **Connection pooling**

### Database Scaling

For high-traffic scenarios:
- **Read replicas** for menu data
- **Connection pooling** optimization
- **Query optimization**
- **Caching strategies**

---

## 🔄 CI/CD Pipeline

### GitHub Actions Workflow

```yaml
# .github/workflows/deploy.yml
name: Deploy Restaurant AI Platform

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: |
          docker-compose -f docker-compose.test.yml up --abort-on-container-exit
  
  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to production
        run: |
          # Your deployment script here
```

### Deployment Strategy

1. **Blue-Green Deployment** for zero downtime
2. **Health checks** before traffic switching
3. **Rollback capability**
4. **Database migrations** handling

---

## 🐛 Troubleshooting

### Common Issues

#### Database Connection Issues
```bash
# Check database container
docker-compose logs postgres

# Test connection
docker-compose exec postgres psql -U restaurant_user -d restaurant_ai_db -c "SELECT 1;"
```

#### Service Not Starting
```bash
# Check service logs
docker-compose logs restaurant-service

# Check resource usage
docker stats
```

#### AI Service Issues
```bash
# Verify OpenAI API key
curl -H "Authorization: Bearer $OPENAI_API_KEY" https://api.openai.com/v1/models

# Check AI service logs
docker-compose logs ai-service
```

### Performance Issues

1. **High CPU Usage**:
   - Scale AI service replicas
   - Optimize database queries
   - Enable Redis caching

2. **Memory Issues**:
   - Increase container memory limits
   - Check for memory leaks in logs
   - Optimize image sizes

3. **Slow Responses**:
   - Enable query profiling
   - Add database indexes
   - Implement response caching

---

## 📈 Backup & Recovery

### Database Backup

```bash
# Create backup
docker-compose exec postgres pg_dump -U restaurant_user restaurant_ai_db > backup.sql

# Restore backup
docker-compose exec -T postgres psql -U restaurant_user restaurant_ai_db < backup.sql
```

### Automated Backups

```bash
# Daily backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
docker-compose exec postgres pg_dump -U restaurant_user restaurant_ai_db | gzip > "backup_$DATE.sql.gz"

# Keep only last 7 days
find . -name "backup_*.sql.gz" -mtime +7 -delete
```

---

## 📞 Support

For deployment issues:
1. Check the troubleshooting section above
2. Review service logs: `docker-compose logs [service-name]`
3. Verify environment configuration
4. Check system resources and dependencies

For production support, ensure you have:
- Monitoring and alerting configured
- Log aggregation setup
- Regular backup procedures
- Incident response plan