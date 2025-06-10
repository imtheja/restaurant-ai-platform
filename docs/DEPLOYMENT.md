# Deployment Guide

> Complete deployment guide for Restaurant AI Platform across development, staging, and production environments

## Table of Contents

1. [Overview](#overview)
2. [Environment Setup](#environment-setup)
3. [Local Development](#local-development)
4. [Docker Deployment](#docker-deployment)
5. [Kubernetes Deployment](#kubernetes-deployment)
6. [Cloud Provider Deployment](#cloud-provider-deployment)
7. [CI/CD Pipeline](#cicd-pipeline)
8. [Monitoring & Logging](#monitoring--logging)
9. [Backup & Recovery](#backup--recovery)
10. [Troubleshooting](#troubleshooting)

## Overview

The Restaurant AI Platform supports multiple deployment strategies:

- **Local Development**: Docker Compose with hot reloading
- **Docker Production**: Optimized multi-stage containers
- **Kubernetes**: Scalable orchestration with Helm charts
- **Cloud Native**: AWS EKS, Azure AKS, Google GKE
- **Serverless**: AWS Lambda, Azure Functions (planned)

### Deployment Architecture

```mermaid
graph TB
    subgraph "Load Balancer"
        LB[AWS ALB / Azure LB / GCP LB]
    end
    
    subgraph "API Gateway"
        NG[Nginx Ingress]
    end
    
    subgraph "Kubernetes Cluster"
        RS[Restaurant Service Pods]
        MS[Menu Service Pods]
        AIS[AI Service Pods]
        FE[Frontend Pods]
    end
    
    subgraph "Data Layer"
        RDS[(RDS PostgreSQL)]
        REDIS[(ElastiCache Redis)]
        S3[(S3 Storage)]
    end
    
    subgraph "Monitoring"
        PROM[Prometheus]
        GRAF[Grafana]
        ELK[ELK Stack]
    end
    
    LB --> NG
    NG --> RS
    NG --> MS
    NG --> AIS
    NG --> FE
    RS --> RDS
    MS --> RDS
    AIS --> RDS
    RS --> REDIS
    MS --> REDIS
    AIS --> REDIS
    FE --> S3
    RS --> S3
    PROM --> RS
    PROM --> MS
    PROM --> AIS
    GRAF --> PROM
    ELK --> RS
    ELK --> MS
    ELK --> AIS
```

## Environment Setup

### Prerequisites

#### Required Software
```bash
# Container Runtime
Docker Desktop 4.0+ or Docker Engine 20.10+
Docker Compose 2.0+

# Kubernetes (for K8s deployment)
kubectl 1.24+
Helm 3.8+

# Development Tools
Node.js 18.0+
Python 3.11+
Git 2.30+

# Cloud CLI Tools (optional)
AWS CLI 2.0+
Azure CLI 2.40+
Google Cloud SDK 400.0+
```

#### System Requirements

**Development Environment:**
- CPU: 4+ cores
- RAM: 8GB minimum, 16GB recommended
- Storage: 20GB+ available space
- OS: macOS, Linux, Windows with WSL2

**Production Environment:**
- CPU: 8+ cores per node
- RAM: 16GB+ per node
- Storage: 100GB+ SSD
- Network: 1Gbps+ bandwidth

### Environment Variables

#### Core Configuration
```bash
# Application
NODE_ENV=production
DEBUG=false
PORT=3000

# Database
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=restaurant_ai
POSTGRES_USER=restaurant_user
POSTGRES_PASSWORD=secure_password_here
DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=redis_password_here
REDIS_URL=redis://:${REDIS_PASSWORD}@${REDIS_HOST}:${REDIS_PORT}/0

# AI Services
AI_PROVIDER=groq  # openai, groq, grok
GROQ_API_KEY=gsk_your_groq_api_key_here
OPENAI_API_KEY=sk-your_openai_api_key_here
GROK_API_KEY=xai-your_grok_api_key_here

# Security
JWT_SECRET_KEY=your_super_secret_jwt_key_minimum_32_characters
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440

# CORS
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com
CORS_ALLOW_CREDENTIALS=true

# File Storage
STORAGE_TYPE=s3  # local, s3, azure, gcp
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=us-west-2
S3_BUCKET=restaurant-ai-uploads

# Monitoring
PROMETHEUS_ENABLED=true
JAEGER_ENABLED=true
LOG_LEVEL=INFO
```

#### Environment-Specific Variables

**Development (.env.dev)**
```bash
NODE_ENV=development
DEBUG=true
LOG_LEVEL=DEBUG
POSTGRES_HOST=localhost
REDIS_HOST=localhost
AI_PROVIDER=groq
CORS_ORIGINS=http://localhost:3000
```

**Staging (.env.staging)**
```bash
NODE_ENV=staging
DEBUG=false
LOG_LEVEL=INFO
POSTGRES_HOST=staging-db.example.com
REDIS_HOST=staging-redis.example.com
AI_PROVIDER=groq
CORS_ORIGINS=https://staging.yourdomain.com
```

**Production (.env.prod)**
```bash
NODE_ENV=production
DEBUG=false
LOG_LEVEL=WARN
POSTGRES_HOST=prod-db.example.com
REDIS_HOST=prod-redis.example.com
AI_PROVIDER=openai
CORS_ORIGINS=https://yourdomain.com
```

## Local Development

### Quick Start
```bash
# Clone repository
git clone https://github.com/your-org/restaurant-ai-platform.git
cd restaurant-ai-platform

# Copy environment files
cp .env.example .env
cp frontend/.env.example frontend/.env

# Start infrastructure services
docker-compose up -d postgres redis

# Install dependencies
cd backend && pip install -r requirements.txt
cd ../frontend && npm install

# Initialize database
python scripts/init_db.py
python scripts/load_cookie_shop.py

# Start development servers
npm run dev:all
```

### Development Commands
```bash
# Start all services
npm run dev:all

# Start individual services
npm run dev:restaurant-service
npm run dev:menu-service
npm run dev:ai-service
npm run dev:frontend

# Run tests
npm run test
npm run test:backend
npm run test:frontend
npm run test:e2e

# Code quality
npm run lint
npm run format
npm run type-check

# Database operations
npm run db:migrate
npm run db:seed
npm run db:reset
```

### Development Docker Compose
```yaml
# docker-compose.dev.yml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: restaurant_ai_dev
      POSTGRES_USER: dev_user
      POSTGRES_PASSWORD: dev_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_dev_data:/var/lib/postgresql/data
      - ./backend/shared/database/init.sql:/docker-entrypoint-initdb.d/init.sql

  redis:
    image: redis:7-alpine
    command: redis-server --requirepass dev_password
    ports:
      - "6379:6379"
    volumes:
      - redis_dev_data:/data

  restaurant-service:
    build:
      context: ./backend/restaurant-service
      dockerfile: Dockerfile.dev
    ports:
      - "8001:8001"
    environment:
      - DATABASE_URL=postgresql://dev_user:dev_password@postgres:5432/restaurant_ai_dev
      - REDIS_URL=redis://:dev_password@redis:6379/0
    volumes:
      - ./backend:/app
    depends_on:
      - postgres
      - redis
    command: uvicorn main:app --host 0.0.0.0 --port 8001 --reload

volumes:
  postgres_dev_data:
  redis_dev_data:
```

## Docker Deployment

### Production Docker Build

#### Multi-stage Dockerfile (Backend)
```dockerfile
# backend/restaurant-service/Dockerfile
FROM python:3.11-slim as builder

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Production stage
FROM python:3.11-slim

WORKDIR /app

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copy installed packages from builder
COPY --from=builder /root/.local /home/appuser/.local

# Copy application code
COPY . .

# Set ownership and permissions
RUN chown -R appuser:appuser /app
USER appuser

# Add local packages to PATH
ENV PATH=/home/appuser/.local/bin:$PATH

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8001/health || exit 1

# Expose port
EXPOSE 8001

# Start application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
```

#### Multi-stage Dockerfile (Frontend)
```dockerfile
# frontend/Dockerfile
FROM node:18-alpine as builder

WORKDIR /app

# Copy package files
COPY package*.json ./
RUN npm ci --only=production

# Copy source code
COPY . .

# Build application
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built application
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost || exit 1

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

### Production Docker Compose
```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./infrastructure/nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./infrastructure/nginx/default.conf:/etc/nginx/conf.d/default.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - frontend
      - restaurant-service
      - menu-service
      - ai-service

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    environment:
      - NODE_ENV=production
    restart: unless-stopped

  restaurant-service:
    build:
      context: ./backend/restaurant-service
      dockerfile: Dockerfile
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
    restart: unless-stopped
    depends_on:
      - postgres
      - redis

  menu-service:
    build:
      context: ./backend/menu-service
      dockerfile: Dockerfile
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
    restart: unless-stopped
    depends_on:
      - postgres
      - redis

  ai-service:
    build:
      context: ./backend/ai-service
      dockerfile: Dockerfile
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - AI_PROVIDER=${AI_PROVIDER}
      - GROQ_API_KEY=${GROQ_API_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    restart: unless-stopped
    depends_on:
      - postgres
      - redis

  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=${POSTGRES_DB}
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    command: redis-server --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    restart: unless-stopped

  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    restart: unless-stopped

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana:/etc/grafana/provisioning
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
  prometheus_data:
  grafana_data:
```

### Deployment Commands
```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Start production stack
docker-compose -f docker-compose.prod.yml up -d

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Scale services
docker-compose -f docker-compose.prod.yml up -d --scale restaurant-service=3

# Update services
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d

# Backup database
docker-compose -f docker-compose.prod.yml exec postgres pg_dump -U ${POSTGRES_USER} ${POSTGRES_DB} > backup_$(date +%Y%m%d_%H%M%S).sql
```

## Kubernetes Deployment

### Helm Chart Structure
```
infrastructure/kubernetes/helm-charts/restaurant-ai/
├── Chart.yaml
├── values.yaml
├── values-staging.yaml
├── values-production.yaml
├── templates/
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── ingress.yaml
│   ├── configmap.yaml
│   ├── secret.yaml
│   ├── hpa.yaml
│   ├── pdb.yaml
│   └── servicemonitor.yaml
└── charts/
    ├── postgresql/
    ├── redis/
    └── nginx-ingress/
```

#### Chart.yaml
```yaml
apiVersion: v2
name: restaurant-ai
description: Restaurant AI Platform Helm Chart
type: application
version: 0.1.0
appVersion: "1.0.0"

dependencies:
  - name: postgresql
    version: 12.1.9
    repository: https://charts.bitnami.com/bitnami
    condition: postgresql.enabled

  - name: redis
    version: 17.3.7
    repository: https://charts.bitnami.com/bitnami
    condition: redis.enabled

  - name: nginx-ingress
    version: 4.4.0
    repository: https://kubernetes.github.io/ingress-nginx
    condition: ingress-nginx.enabled
```

#### values.yaml
```yaml
# Global configuration
global:
  imageRegistry: ""
  imagePullSecrets: []
  storageClass: ""

# Application configuration
replicaCount: 3

image:
  registry: your-registry.com
  repository: restaurant-ai
  tag: "latest"
  pullPolicy: IfNotPresent

nameOverride: ""
fullnameOverride: ""

serviceAccount:
  create: true
  annotations: {}
  name: ""

podAnnotations: {}
podSecurityContext:
  fsGroup: 2000

securityContext:
  capabilities:
    drop:
    - ALL
  readOnlyRootFilesystem: true
  runAsNonRoot: true
  runAsUser: 1000

service:
  type: ClusterIP
  port: 80

ingress:
  enabled: true
  className: "nginx"
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/rate-limit: "100"
  hosts:
    - host: restaurant-ai.example.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: restaurant-ai-tls
      hosts:
        - restaurant-ai.example.com

resources:
  limits:
    cpu: 1000m
    memory: 1Gi
  requests:
    cpu: 500m
    memory: 512Mi

autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 20
  targetCPUUtilizationPercentage: 70
  targetMemoryUtilizationPercentage: 80

nodeSelector: {}
tolerations: []
affinity: {}

# Database configuration
postgresql:
  enabled: true
  auth:
    postgresPassword: "secure_password"
    username: "restaurant_user"
    password: "user_password"
    database: "restaurant_ai"
  primary:
    persistence:
      enabled: true
      size: 100Gi
    resources:
      requests:
        memory: 1Gi
        cpu: 500m

# Redis configuration
redis:
  enabled: true
  auth:
    enabled: true
    password: "redis_password"
  master:
    persistence:
      enabled: true
      size: 50Gi
    resources:
      requests:
        memory: 512Mi
        cpu: 250m

# Environment variables
env:
  NODE_ENV: production
  LOG_LEVEL: INFO
  AI_PROVIDER: groq

# Secrets
secrets:
  JWT_SECRET_KEY: "your_jwt_secret"
  GROQ_API_KEY: "your_groq_key"
  DATABASE_URL: "postgresql://user:pass@host:5432/db"

# ConfigMaps
config:
  CORS_ORIGINS: "https://restaurant-ai.example.com"
  PROMETHEUS_ENABLED: "true"
```

#### Deployment Template
```yaml
# templates/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "restaurant-ai.fullname" . }}
  labels:
    {{- include "restaurant-ai.labels" . | nindent 4 }}
spec:
  {{- if not .Values.autoscaling.enabled }}
  replicas: {{ .Values.replicaCount }}
  {{- end }}
  selector:
    matchLabels:
      {{- include "restaurant-ai.selectorLabels" . | nindent 6 }}
  template:
    metadata:
      annotations:
        checksum/config: {{ include (print $.Template.BasePath "/configmap.yaml") . | sha256sum }}
        {{- with .Values.podAnnotations }}
        {{- toYaml . | nindent 8 }}
        {{- end }}
      labels:
        {{- include "restaurant-ai.selectorLabels" . | nindent 8 }}
    spec:
      {{- with .Values.imagePullSecrets }}
      imagePullSecrets:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      serviceAccountName: {{ include "restaurant-ai.serviceAccountName" . }}
      securityContext:
        {{- toYaml .Values.podSecurityContext | nindent 8 }}
      containers:
        - name: restaurant-service
          securityContext:
            {{- toYaml .Values.securityContext | nindent 12 }}
          image: "{{ .Values.image.registry }}/{{ .Values.image.repository }}/restaurant-service:{{ .Values.image.tag }}"
          imagePullPolicy: {{ .Values.image.pullPolicy }}
          ports:
            - name: http
              containerPort: 8001
              protocol: TCP
          livenessProbe:
            httpGet:
              path: /health
              port: http
            initialDelaySeconds: 30
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /health
              port: http
            initialDelaySeconds: 5
            periodSeconds: 5
          env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: {{ include "restaurant-ai.fullname" . }}-secret
                  key: DATABASE_URL
            - name: JWT_SECRET_KEY
              valueFrom:
                secretKeyRef:
                  name: {{ include "restaurant-ai.fullname" . }}-secret
                  key: JWT_SECRET_KEY
          envFrom:
            - configMapRef:
                name: {{ include "restaurant-ai.fullname" . }}-config
          resources:
            {{- toYaml .Values.resources | nindent 12 }}
      {{- with .Values.nodeSelector }}
      nodeSelector:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      {{- with .Values.affinity }}
      affinity:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      {{- with .Values.tolerations }}
      tolerations:
        {{- toYaml . | nindent 8 }}
      {{- end }}
```

### Kubernetes Deployment Commands
```bash
# Add Helm repositories
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update

# Install dependencies
helm dependency update infrastructure/kubernetes/helm-charts/restaurant-ai/

# Deploy to staging
helm install restaurant-ai-staging \
  ./infrastructure/kubernetes/helm-charts/restaurant-ai/ \
  --namespace staging \
  --create-namespace \
  --values ./infrastructure/kubernetes/helm-charts/restaurant-ai/values-staging.yaml

# Deploy to production
helm install restaurant-ai-prod \
  ./infrastructure/kubernetes/helm-charts/restaurant-ai/ \
  --namespace production \
  --create-namespace \
  --values ./infrastructure/kubernetes/helm-charts/restaurant-ai/values-production.yaml

# Upgrade deployment
helm upgrade restaurant-ai-prod \
  ./infrastructure/kubernetes/helm-charts/restaurant-ai/ \
  --namespace production \
  --values ./infrastructure/kubernetes/helm-charts/restaurant-ai/values-production.yaml

# Rollback deployment
helm rollback restaurant-ai-prod 1 --namespace production

# Check deployment status
kubectl get pods -n production
kubectl get services -n production
kubectl get ingress -n production

# Scale deployment
kubectl scale deployment restaurant-ai-prod-restaurant-service --replicas=5 -n production

# Check logs
kubectl logs -f deployment/restaurant-ai-prod-restaurant-service -n production
```

## Cloud Provider Deployment

### AWS EKS Deployment

#### Create EKS Cluster
```bash
# Install eksctl
curl --silent --location "https://github.com/weaveworks/eksctl/releases/latest/download/eksctl_$(uname -s)_amd64.tar.gz" | tar xz -C /tmp
sudo mv /tmp/eksctl /usr/local/bin

# Create cluster
eksctl create cluster \
  --name restaurant-ai-cluster \
  --region us-west-2 \
  --nodes 3 \
  --node-type t3.large \
  --with-oidc \
  --managed \
  --vpc-cidr 172.16.0.0/16

# Configure kubectl
aws eks update-kubeconfig --region us-west-2 --name restaurant-ai-cluster

# Install AWS Load Balancer Controller
eksctl utils associate-iam-oidc-provider --region us-west-2 --cluster restaurant-ai-cluster --approve

curl -o iam_policy.json https://raw.githubusercontent.com/kubernetes-sigs/aws-load-balancer-controller/v2.4.4/docs/install/iam_policy.json

aws iam create-policy \
    --policy-name AWSLoadBalancerControllerIAMPolicy \
    --policy-document file://iam_policy.json

eksctl create iamserviceaccount \
  --cluster=restaurant-ai-cluster \
  --namespace=kube-system \
  --name=aws-load-balancer-controller \
  --attach-policy-arn=arn:aws:iam::ACCOUNT-ID:policy/AWSLoadBalancerControllerIAMPolicy \
  --override-existing-serviceaccounts \
  --approve

helm install aws-load-balancer-controller eks/aws-load-balancer-controller \
  -n kube-system \
  --set clusterName=restaurant-ai-cluster \
  --set serviceAccount.create=false \
  --set serviceAccount.name=aws-load-balancer-controller
```

#### RDS Database Setup
```bash
# Create RDS subnet group
aws rds create-db-subnet-group \
  --db-subnet-group-name restaurant-ai-subnet-group \
  --db-subnet-group-description "Subnet group for Restaurant AI" \
  --subnet-ids subnet-12345678 subnet-87654321

# Create RDS instance
aws rds create-db-instance \
  --db-instance-identifier restaurant-ai-prod \
  --db-instance-class db.t3.medium \
  --engine postgres \
  --engine-version 15.3 \
  --master-username postgres \
  --master-user-password YourSecurePassword123 \
  --allocated-storage 100 \
  --storage-type gp2 \
  --db-subnet-group-name restaurant-ai-subnet-group \
  --vpc-security-group-ids sg-12345678 \
  --backup-retention-period 7 \
  --multi-az \
  --storage-encrypted
```

#### ElastiCache Redis Setup
```bash
# Create Redis cluster
aws elasticache create-replication-group \
  --replication-group-id restaurant-ai-redis \
  --description "Redis cluster for Restaurant AI" \
  --num-cache-clusters 2 \
  --cache-node-type cache.t3.micro \
  --engine redis \
  --engine-version 7.0 \
  --port 6379 \
  --cache-subnet-group-name restaurant-ai-cache-subnet-group \
  --security-group-ids sg-12345678 \
  --at-rest-encryption-enabled \
  --transit-encryption-enabled
```

### Azure AKS Deployment

#### Create AKS Cluster
```bash
# Create resource group
az group create --name restaurant-ai-rg --location westus2

# Create AKS cluster
az aks create \
  --resource-group restaurant-ai-rg \
  --name restaurant-ai-cluster \
  --node-count 3 \
  --node-vm-size Standard_D4s_v3 \
  --enable-addons monitoring \
  --generate-ssh-keys \
  --network-plugin azure \
  --network-policy azure

# Get credentials
az aks get-credentials --resource-group restaurant-ai-rg --name restaurant-ai-cluster

# Install NGINX Ingress Controller
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm install nginx-ingress ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --create-namespace \
  --set controller.replicaCount=2
```

#### Azure Database for PostgreSQL
```bash
# Create PostgreSQL server
az postgres server create \
  --resource-group restaurant-ai-rg \
  --name restaurant-ai-postgres \
  --location westus2 \
  --admin-user postgres \
  --admin-password YourSecurePassword123 \
  --sku-name GP_Gen5_2 \
  --version 15

# Create database
az postgres db create \
  --resource-group restaurant-ai-rg \
  --server-name restaurant-ai-postgres \
  --name restaurant_ai
```

### Google GKE Deployment

#### Create GKE Cluster
```bash
# Enable APIs
gcloud services enable container.googleapis.com

# Create cluster
gcloud container clusters create restaurant-ai-cluster \
  --num-nodes=3 \
  --machine-type=e2-standard-4 \
  --region=us-west1 \
  --enable-autoscaling \
  --min-nodes=1 \
  --max-nodes=10 \
  --enable-autorepair \
  --enable-autoupgrade

# Get credentials
gcloud container clusters get-credentials restaurant-ai-cluster --region=us-west1

# Install NGINX Ingress
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.2/deploy/static/provider/cloud/deploy.yaml
```

## CI/CD Pipeline

### GitHub Actions Workflow
```yaml
# .github/workflows/deploy.yml
name: Deploy Restaurant AI Platform

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: test
          POSTGRES_DB: test_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

      redis:
        image: redis:7
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 6379:6379

    steps:
    - uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Set up Node.js
      uses: actions/setup-node@v4
      with:
        node-version: '18'

    - name: Install Python dependencies
      run: |
        cd backend
        python -m pip install --upgrade pip
        pip install -r requirements.txt

    - name: Install Node dependencies
      run: |
        cd frontend
        npm ci

    - name: Run Python tests
      run: |
        cd backend
        pytest tests/ --cov=. --cov-report=xml
      env:
        DATABASE_URL: postgresql://postgres:test@localhost:5432/test_db
        REDIS_URL: redis://localhost:6379/0

    - name: Run Node tests
      run: |
        cd frontend
        npm run test:ci

    - name: Run E2E tests
      run: |
        docker-compose -f docker-compose.test.yml up -d
        npm run test:e2e
        docker-compose -f docker-compose.test.yml down

  build:
    needs: test
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write

    steps:
    - name: Checkout repository
      uses: actions/checkout@v4

    - name: Log in to Container Registry
      uses: docker/login-action@v3
      with:
        registry: ${{ env.REGISTRY }}
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}

    - name: Extract metadata
      id: meta
      uses: docker/metadata-action@v5
      with:
        images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
        tags: |
          type=ref,event=branch
          type=ref,event=pr
          type=sha,prefix={{branch}}-

    - name: Build and push Docker images
      uses: docker/build-push-action@v5
      with:
        context: .
        file: ./Dockerfile.multi
        push: true
        tags: ${{ steps.meta.outputs.tags }}
        labels: ${{ steps.meta.outputs.labels }}

  deploy-staging:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/develop'
    environment: staging

    steps:
    - name: Checkout repository
      uses: actions/checkout@v4

    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v4
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: us-west-2

    - name: Update kubeconfig
      run: |
        aws eks update-kubeconfig --region us-west-2 --name restaurant-ai-staging

    - name: Deploy to staging
      run: |
        helm upgrade --install restaurant-ai-staging \
          ./infrastructure/kubernetes/helm-charts/restaurant-ai/ \
          --namespace staging \
          --create-namespace \
          --values ./infrastructure/kubernetes/helm-charts/restaurant-ai/values-staging.yaml \
          --set image.tag=${GITHUB_SHA:0:7}

  deploy-production:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    environment: production

    steps:
    - name: Checkout repository
      uses: actions/checkout@v4

    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v4
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: us-west-2

    - name: Update kubeconfig
      run: |
        aws eks update-kubeconfig --region us-west-2 --name restaurant-ai-prod

    - name: Deploy to production
      run: |
        helm upgrade --install restaurant-ai-prod \
          ./infrastructure/kubernetes/helm-charts/restaurant-ai/ \
          --namespace production \
          --create-namespace \
          --values ./infrastructure/kubernetes/helm-charts/restaurant-ai/values-production.yaml \
          --set image.tag=${GITHUB_SHA:0:7}

    - name: Verify deployment
      run: |
        kubectl rollout status deployment/restaurant-ai-prod-restaurant-service -n production
        kubectl get pods -n production
```

## Monitoring & Logging

### Prometheus Configuration
```yaml
# monitoring/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "alert_rules.yml"

scrape_configs:
  - job_name: 'restaurant-service'
    static_configs:
      - targets: ['restaurant-service:8001']
    metrics_path: /metrics

  - job_name: 'menu-service'
    static_configs:
      - targets: ['menu-service:8002']
    metrics_path: /metrics

  - job_name: 'ai-service'
    static_configs:
      - targets: ['ai-service:8003']
    metrics_path: /metrics

  - job_name: 'kubernetes-pods'
    kubernetes_sd_configs:
      - role: pod
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
        action: keep
        regex: true

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093
```

### Grafana Dashboards
```json
{
  "dashboard": {
    "id": null,
    "title": "Restaurant AI Platform",
    "tags": ["restaurant-ai"],
    "timezone": "browser",
    "panels": [
      {
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])",
            "legendFormat": "{{method}} {{endpoint}}"
          }
        ]
      },
      {
        "title": "Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "95th percentile"
          }
        ]
      },
      {
        "title": "Active Conversations",
        "type": "singlestat",
        "targets": [
          {
            "expr": "active_conversations_total",
            "legendFormat": "Active Conversations"
          }
        ]
      }
    ]
  }
}
```

### ELK Stack Configuration
```yaml
# monitoring/logstash.conf
input {
  beats {
    port => 5044
  }
}

filter {
  if [fields][service] == "restaurant-ai" {
    json {
      source => "message"
    }
    
    date {
      match => [ "timestamp", "ISO8601" ]
    }
    
    mutate {
      add_field => { "service_name" => "%{[fields][service_name]}" }
    }
  }
}

output {
  elasticsearch {
    hosts => ["elasticsearch:9200"]
    index => "restaurant-ai-%{+YYYY.MM.dd}"
  }
}
```

## Backup & Recovery

### Database Backup
```bash
#!/bin/bash
# scripts/backup_database.sh

set -e

BACKUP_DIR="/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="restaurant_ai_backup_${TIMESTAMP}.sql"

# Create backup directory if not exists
mkdir -p ${BACKUP_DIR}

# Backup database
pg_dump -h ${POSTGRES_HOST} -U ${POSTGRES_USER} -d ${POSTGRES_DB} \
  --verbose --clean --no-owner --no-acl \
  --file=${BACKUP_DIR}/${BACKUP_FILE}

# Compress backup
gzip ${BACKUP_DIR}/${BACKUP_FILE}

# Upload to S3
aws s3 cp ${BACKUP_DIR}/${BACKUP_FILE}.gz \
  s3://${S3_BACKUP_BUCKET}/database/${BACKUP_FILE}.gz

# Keep only last 30 days of local backups
find ${BACKUP_DIR} -name "restaurant_ai_backup_*.sql.gz" -mtime +30 -delete

echo "Backup completed: ${BACKUP_FILE}.gz"
```

### Disaster Recovery Plan
```bash
#!/bin/bash
# scripts/restore_database.sh

set -e

BACKUP_FILE=$1
RESTORE_DB=${2:-restaurant_ai_restore}

if [ -z "$BACKUP_FILE" ]; then
  echo "Usage: $0 <backup_file> [restore_db_name]"
  exit 1
fi

# Download backup from S3
aws s3 cp s3://${S3_BACKUP_BUCKET}/database/${BACKUP_FILE} ./

# Decompress backup
gunzip ${BACKUP_FILE}
BACKUP_FILE_UNCOMPRESSED=${BACKUP_FILE%.gz}

# Create restore database
createdb -h ${POSTGRES_HOST} -U ${POSTGRES_USER} ${RESTORE_DB}

# Restore database
psql -h ${POSTGRES_HOST} -U ${POSTGRES_USER} -d ${RESTORE_DB} \
  -f ${BACKUP_FILE_UNCOMPRESSED}

echo "Database restored to: ${RESTORE_DB}"
```

### Kubernetes Backup with Velero
```bash
# Install Velero
kubectl apply -f https://github.com/vmware-tanzu/velero/releases/download/v1.12.0/00-prereqs.yaml

# Create backup
velero backup create restaurant-ai-backup \
  --include-namespaces production \
  --storage-location default

# Restore backup
velero restore create --from-backup restaurant-ai-backup
```

## Troubleshooting

### Common Issues

#### Database Connection Issues
```bash
# Check database connectivity
kubectl exec -it deployment/restaurant-ai-prod-restaurant-service -n production -- \
  python -c "
import psycopg2
try:
    conn = psycopg2.connect('${DATABASE_URL}')
    print('Database connection successful')
    conn.close()
except Exception as e:
    print(f'Database connection failed: {e}')
"
```

#### Service Discovery Issues
```bash
# Check service endpoints
kubectl get endpoints -n production

# Check DNS resolution
kubectl exec -it deployment/restaurant-ai-prod-restaurant-service -n production -- \
  nslookup restaurant-ai-prod-postgresql.production.svc.cluster.local

# Check ingress
kubectl describe ingress restaurant-ai-prod -n production
```

#### Performance Issues
```bash
# Check resource usage
kubectl top pods -n production
kubectl top nodes

# Check HPA status
kubectl get hpa -n production

# Check events
kubectl get events --sort-by=.metadata.creationTimestamp -n production
```

### Debug Commands
```bash
# Access pod shell
kubectl exec -it deployment/restaurant-ai-prod-restaurant-service -n production -- /bin/bash

# View real-time logs
kubectl logs -f deployment/restaurant-ai-prod-restaurant-service -n production

# Port forward for local debugging
kubectl port-forward deployment/restaurant-ai-prod-restaurant-service 8001:8001 -n production

# Check ConfigMaps and Secrets
kubectl get configmap restaurant-ai-prod-config -n production -o yaml
kubectl get secret restaurant-ai-prod-secret -n production -o yaml
```

### Health Checks
```bash
# Check all components
kubectl get pods,services,ingress,hpa -n production

# Check application health
curl -f http://localhost/health

# Check metrics endpoint
curl http://localhost/metrics
```

---

This deployment guide provides comprehensive instructions for deploying the Restaurant AI Platform across various environments and cloud providers. Follow the specific sections relevant to your deployment strategy and infrastructure requirements.