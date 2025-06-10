# Restaurant AI Platform 🍽️🤖

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![Node.js](https://img.shields.io/badge/Node.js-18+-green.svg)](https://nodejs.org)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://docker.com)
[![Kubernetes](https://img.shields.io/badge/Kubernetes-Ready-blue.svg)](https://kubernetes.io)

> An enterprise-grade, AI-powered restaurant platform built with microservices architecture. Enables restaurants to provide intelligent, conversational experiences to customers through speech-enabled AI assistants, dynamic menu management, and real-time interactions.

## 🚀 Live Demo
- **Demo Restaurant**: [The Cookie Jar](http://localhost:3000/r/the-cookie-jar)
- **Admin Dashboard**: [Restaurant Management](http://localhost:3000/admin)
- **API Documentation**: [Interactive Swagger Docs](http://localhost:8001/docs)

## 📋 Table of Contents

1. [System Architecture](#-system-architecture)
2. [Technology Stack](#-technology-stack)
3. [Features](#-features)
4. [Quick Start](#-quick-start)
5. [Development Guide](#-development-guide)
6. [Deployment](#-deployment)
7. [API Documentation](#-api-documentation)
8. [Security](#-security)
9. [Monitoring & Analytics](#-monitoring--analytics)
10. [Contributing](#-contributing)
11. [License](#-license)

## 🏗️ System Architecture

### Microservices Overview

```mermaid
graph TB
    subgraph "Frontend Layer"
        FE[React TypeScript Frontend]
        PWA[Progressive Web App]
    end
    
    subgraph "API Gateway"
        NG[Nginx Reverse Proxy]
        LB[Load Balancer]
    end
    
    subgraph "Microservices"
        RS[Restaurant Service :8001]
        MS[Menu Service :8002] 
        AIS[AI Service :8003]
    end
    
    subgraph "Data Layer"
        PG[(PostgreSQL)]
        RD[(Redis Cache)]
        ES[(Elasticsearch)]
    end
    
    subgraph "External Services"
        AI[OpenAI/Groq API]
        CDN[CloudFront CDN]
        S3[AWS S3 Storage]
    end
    
    FE --> NG
    PWA --> NG
    NG --> RS
    NG --> MS  
    NG --> AIS
    RS --> PG
    MS --> PG
    AIS --> PG
    AIS --> AI
    RS --> RD
    MS --> RD
    AIS --> RD
    RS --> ES
    MS --> ES
    FE --> CDN
    RS --> S3
```

### Component Architecture

```mermaid
graph LR
    subgraph "Restaurant Service"
        RC[Restaurant Controller]
        RM[Restaurant Model]
        RR[Restaurant Repository]
    end
    
    subgraph "Menu Service"
        MC[Menu Controller]
        MM[Menu Model]
        MR[Menu Repository]
        IC[Ingredient Controller]
    end
    
    subgraph "AI Service"
        CC[Chat Controller]
        AI[AI Service]
        CM[Conversation Model]
        AM[Analytics Model]
    end
    
    subgraph "Shared Layer"
        DB[Database Models]
        UT[Utilities]
        SC[Schemas]
        MW[Middleware]
    end
    
    RC --> RM
    RM --> RR
    MC --> MM
    MM --> MR
    CC --> AI
    AI --> CM
    AI --> AM
    RC --> DB
    MC --> DB
    CC --> DB
```

## 🛠️ Technology Stack

### Backend Technologies
- **Framework**: FastAPI 0.104+ (Python 3.11+)
- **Database**: PostgreSQL 15+ with SQLAlchemy ORM
- **Cache**: Redis 7+ for session management and caching
- **Search**: Elasticsearch 8+ for advanced search capabilities
- **AI/ML**: OpenAI GPT-4, Groq, or local LLM integration
- **Task Queue**: Celery with Redis broker
- **Authentication**: JWT with OAuth2 integration
- **API Documentation**: OpenAPI 3.0 with Swagger UI

### Frontend Technologies
- **Framework**: React 18+ with TypeScript 5+
- **Build Tool**: Vite 5+ for fast development and builds
- **UI Library**: Material-UI (MUI) 5+ with custom theming
- **State Management**: React Query + Zustand
- **Routing**: React Router v6
- **Animations**: Framer Motion
- **Speech**: Web Speech API (SpeechRecognition & SpeechSynthesis)
- **PWA**: Service Workers with Workbox

### DevOps & Infrastructure
- **Containerization**: Docker with multi-stage builds
- **Orchestration**: Kubernetes with Helm charts
- **Reverse Proxy**: Nginx with SSL termination
- **CI/CD**: GitHub Actions with automated testing
- **Monitoring**: Prometheus + Grafana + Jaeger
- **Logging**: ELK Stack (Elasticsearch, Logstash, Kibana)
- **Cloud Providers**: AWS, Azure, GCP ready

### Development Tools
- **Code Quality**: Pre-commit hooks, Black, Pylint, ESLint
- **Testing**: Pytest, Jest, Playwright for E2E
- **Documentation**: Sphinx for Python, JSDoc for TypeScript
- **Version Control**: Git with conventional commits

## ✨ Features

### 🎯 Core Features (MVP)
- ✅ **Intelligent AI Assistant**: Speech-enabled conversational AI with personality
- ✅ **Dynamic Menu Management**: Real-time menu updates with rich media support
- ✅ **Multi-Restaurant Support**: Single platform serving multiple restaurants
- ✅ **Responsive Design**: Mobile-first PWA with offline capabilities
- ✅ **Real-time Chat**: WebSocket-based instant messaging
- ✅ **Allergen Management**: Comprehensive allergen tracking and warnings
- ✅ **Analytics Dashboard**: Real-time insights and customer behavior tracking

### 🚀 Advanced Features (Phase 2)
- 🔄 **User Authentication**: Multi-factor authentication with social login
- 🔄 **Order Management**: Complete POS integration with payment processing
- 🔄 **Inventory Tracking**: Real-time stock management with automatic reordering
- 🔄 **Multi-language Support**: Internationalization with automatic translation
- 🔄 **Voice Ordering**: Complete voice-to-order workflow
- 🔄 **Advanced Analytics**: ML-powered recommendations and insights

### 🎨 UI/UX Features
- 🌈 **Vibrant Design**: Colorful, bakery-inspired design system
- 🎭 **Animated Interactions**: Smooth transitions and micro-interactions
- 📱 **Mobile Optimized**: Touch-friendly interfaces with gesture support
- 🎤 **Voice Interface**: Hands-free interaction with speech feedback
- 🔊 **Audio Feedback**: Natural speech synthesis with personality
- 👥 **Accessibility**: WCAG 2.1 compliant with screen reader support

## 🚀 Quick Start

### Prerequisites
```bash
# Required software
- Docker Desktop 4.0+
- Node.js 18+ with npm
- Python 3.11+
- Git

# Optional for local development
- PostgreSQL 15+
- Redis 7+
- VS Code with recommended extensions
```

### 1. Clone and Setup
```bash
git clone https://github.com/your-org/restaurant-ai-platform.git
cd restaurant-ai-platform

# Copy environment configuration
cp .env.example .env
cp frontend/.env.example frontend/.env
```

### 2. Environment Configuration
Edit `.env` file with your configuration:

```bash
# Database Configuration
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=restaurant_ai
POSTGRES_USER=your_user
POSTGRES_PASSWORD=your_password

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password

# AI Service Configuration
AI_PROVIDER=groq  # openai, groq, or grok
GROQ_API_KEY=your_groq_api_key
OPENAI_API_KEY=your_openai_api_key
GROK_API_KEY=your_grok_api_key

# Security
JWT_SECRET_KEY=your_super_secret_jwt_key
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com

# External Services
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
S3_BUCKET=your-bucket-name
```

### 3. Quick Start with Docker (Recommended)
```bash
# Start all services
docker-compose up -d

# Initialize database with sample data
docker-compose exec restaurant-service python /app/scripts/init_db.py
docker-compose exec restaurant-service python /app/scripts/load_cookie_shop.py

# View logs
docker-compose logs -f
```

### 4. Development Mode
```bash
# Start infrastructure services
docker-compose up -d postgres redis nginx

# Install Python dependencies
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Install Node.js dependencies
cd ../frontend
npm install

# Start development servers
npm run dev:all  # Starts all backend services and frontend
```

### 5. Access the Application
- **Frontend**: http://localhost:3000
- **API Gateway**: http://localhost:80
- **Restaurant Service API**: http://localhost:8001/docs
- **Menu Service API**: http://localhost:8002/docs
- **AI Service API**: http://localhost:8003/docs
- **Admin Dashboard**: http://localhost:3000/admin

## 🔧 Development Guide

### Project Structure
```
restaurant-ai-platform/
├── 📁 backend/
│   ├── 📁 restaurant-service/      # Restaurant management microservice
│   │   ├── 📄 main.py             # FastAPI application entry point
│   │   ├── 📁 routers/            # API route handlers
│   │   │   ├── 📄 restaurants.py  # Restaurant CRUD operations
│   │   │   └── 📄 admin.py        # Admin dashboard APIs
│   │   ├── 📁 services/           # Business logic layer
│   │   │   └── 📄 restaurant_service.py
│   │   ├── 📁 middleware/         # Custom middleware
│   │   │   ├── 📄 error_handling.py
│   │   │   ├── 📄 rate_limiting.py
│   │   │   └── 📄 request_logging.py
│   │   ├── 📄 Dockerfile          # Multi-stage Docker build
│   │   └── 📄 requirements.txt    # Python dependencies
│   ├── 📁 menu-service/           # Menu management microservice  
│   │   ├── 📄 main.py
│   │   ├── 📁 routers/
│   │   │   ├── 📄 menu.py         # Menu CRUD operations
│   │   │   └── 📄 ingredients.py  # Ingredient management
│   │   └── 📁 services/           # Menu business logic
│   ├── 📁 ai-service/             # AI conversation microservice
│   │   ├── 📄 main.py
│   │   ├── 📁 routers/
│   │   │   ├── 📄 chat.py         # Chat endpoints
│   │   │   └── 📄 conversations.py # Conversation management
│   │   ├── 📁 services/
│   │   │   └── 📄 ai_service.py   # AI integration logic
│   │   └── 📄 requirements.txt
│   └── 📁 shared/                 # Shared utilities and models
│       ├── 📁 database/
│       │   ├── 📄 connection.py   # Database connection management
│       │   ├── 📄 models.py       # SQLAlchemy models
│       │   └── 📄 init.sql        # Database schema
│       ├── 📄 schemas.py          # Pydantic schemas
│       └── 📄 utils.py            # Common utilities
├── 📁 frontend/                   # React TypeScript application
│   ├── 📁 src/
│   │   ├── 📄 App.tsx             # Main application component
│   │   ├── 📁 components/         # Reusable UI components
│   │   │   ├── 📁 chat/           # AI chat components
│   │   │   │   ├── 📄 ChatInterface.tsx
│   │   │   │   ├── 📄 FloatingAIAssistant.tsx
│   │   │   │   └── 📄 MenuItemAIPopup.tsx
│   │   │   ├── 📁 menu/           # Menu display components
│   │   │   │   ├── 📄 MenuDisplay.tsx
│   │   │   │   └── 📄 MenuItemCard.tsx
│   │   │   └── 📁 restaurant/     # Restaurant components
│   │   │       ├── 📄 RestaurantHeader.tsx
│   │   │       └── 📄 RestaurantPage.tsx
│   │   ├── 📁 pages/              # Route-level components
│   │   │   └── 📄 RestaurantPage.tsx
│   │   ├── 📁 services/           # API integration
│   │   │   └── 📄 api.ts          # Axios-based API client
│   │   ├── 📁 store/              # State management
│   │   │   └── 📄 themeStore.ts   # Theme configuration
│   │   ├── 📁 types/              # TypeScript definitions
│   │   │   └── 📄 index.ts        # Common type definitions
│   │   └── 📁 utils/              # Frontend utilities
│   ├── 📄 package.json            # Node.js dependencies
│   ├── 📄 tsconfig.json           # TypeScript configuration
│   ├── 📄 vite.config.ts          # Vite build configuration
│   └── 📄 Dockerfile.dev          # Development Docker build
├── 📁 infrastructure/             # Infrastructure as Code
│   ├── 📁 docker/                 # Docker configurations
│   │   ├── 📄 docker-compose.yml  # Development environment
│   │   └── 📄 docker-compose.prod.yml # Production environment
│   ├── 📁 kubernetes/             # Kubernetes manifests
│   │   ├── 📁 helm-charts/        # Helm charts for deployment
│   │   └── 📁 manifests/          # Raw Kubernetes YAML
│   └── 📁 nginx/                  # Nginx configurations
│       ├── 📄 nginx.conf          # Main nginx configuration
│       └── 📄 default.conf        # Site-specific configuration
├── 📁 docs/                       # Comprehensive documentation
│   ├── 📄 API.md                  # API documentation
│   ├── 📄 DEPLOYMENT.md           # Deployment guide
│   ├── 📄 SECURITY.md             # Security implementation
│   └── 📄 CONTRIBUTING.md         # Contribution guidelines
├── 📁 scripts/                    # Utility scripts
│   ├── 📄 init_db.py              # Database initialization
│   ├── 📄 load_cookie_shop.py     # Sample data loading
│   ├── 📄 start_dev.sh            # Development startup script
│   └── 📄 stop_dev.sh             # Development cleanup script
├── 📁 tests/                      # Test suites
│   ├── 📁 backend/                # Backend tests
│   │   ├── 📁 unit/               # Unit tests
│   │   ├── 📁 integration/        # Integration tests
│   │   └── 📁 e2e/                # End-to-end tests
│   └── 📁 frontend/               # Frontend tests
│       ├── 📁 unit/               # Component tests
│       ├── 📁 integration/        # Integration tests
│       └── 📁 e2e/                # Playwright E2E tests
├── 📄 .env.example                # Environment variables template
├── 📄 .gitignore                  # Git ignore patterns
├── 📄 .pre-commit-config.yaml     # Pre-commit hooks configuration
├── 📄 docker-compose.yml          # Main Docker Compose file
├── 📄 docker-compose.prod.yml     # Production Docker Compose
└── 📄 README.md                   # This file
```

### Microservices Communication

#### Service Discovery & Communication
```python
# Service-to-service communication example
import httpx
from fastapi import Depends

class ServiceClient:
    def __init__(self, base_url: str):
        self.client = httpx.AsyncClient(base_url=base_url)
    
    async def get_restaurant_menu(self, restaurant_id: str):
        response = await self.client.get(f"/api/v1/restaurants/{restaurant_id}/menu")
        return response.json()

# Dependency injection for service clients
async def get_menu_service() -> ServiceClient:
    return ServiceClient("http://menu-service:8002")
```

#### API Gateway Configuration (Nginx)
```nginx
# /infrastructure/nginx/default.conf
upstream restaurant-service {
    server restaurant-service:8001;
}

upstream menu-service {
    server menu-service:8002;
}

upstream ai-service {
    server ai-service:8003;
}

server {
    listen 80;
    client_max_body_size 100M;
    
    # Frontend static files
    location / {
        proxy_pass http://frontend:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    # Restaurant service APIs
    location /api/v1/restaurants {
        proxy_pass http://restaurant-service;
        include /etc/nginx/proxy_params;
    }
    
    # Menu service APIs  
    location /api/v1/menu {
        proxy_pass http://menu-service;
        include /etc/nginx/proxy_params;
    }
    
    # AI service APIs
    location /api/v1/chat {
        proxy_pass http://ai-service;
        include /etc/nginx/proxy_params;
    }
    
    # WebSocket support for real-time features
    location /ws {
        proxy_pass http://ai-service;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### Database Design

#### Entity Relationship Diagram
```mermaid
erDiagram
    RESTAURANT ||--o{ MENU_CATEGORY : has
    RESTAURANT ||--o{ CONVERSATION : receives
    RESTAURANT ||--o{ INTERACTION_ANALYTICS : generates
    
    MENU_CATEGORY ||--o{ MENU_ITEM : contains
    MENU_ITEM ||--o{ MENU_ITEM_INGREDIENT : includes
    
    CONVERSATION ||--o{ MESSAGE : contains
    CONVERSATION ||--o{ INTERACTION_ANALYTICS : tracks
    
    INGREDIENT ||--o{ MENU_ITEM_INGREDIENT : used_in
    
    RESTAURANT {
        uuid id PK
        string name
        string slug UK
        string cuisine_type
        text description
        json avatar_config
        json metadata
        boolean is_active
        timestamp created_at
        timestamp updated_at
    }
    
    MENU_CATEGORY {
        uuid id PK
        uuid restaurant_id FK
        string name
        text description
        integer display_order
        boolean is_active
        timestamp created_at
    }
    
    MENU_ITEM {
        uuid id PK
        uuid restaurant_id FK
        uuid category_id FK
        string name
        text description
        decimal price
        string image_url
        boolean is_signature
        integer spice_level
        json allergen_info
        json tags
        integer display_order
        boolean is_available
        timestamp created_at
        timestamp updated_at
    }
    
    INGREDIENT {
        uuid id PK
        uuid restaurant_id FK
        string name
        text description
        json allergen_info
        boolean is_active
        timestamp created_at
    }
    
    CONVERSATION {
        uuid id PK
        uuid restaurant_id FK
        string session_id
        json context
        json metadata
        boolean is_active
        timestamp created_at
        timestamp last_activity
    }
    
    MESSAGE {
        uuid id PK
        uuid conversation_id FK
        string sender_type
        text content
        string message_type
        json meta_data
        timestamp created_at
    }
```

## 🚢 Deployment

### Production Deployment with Docker

#### 1. Environment Setup
```bash
# Production environment variables
export NODE_ENV=production
export POSTGRES_HOST=your-db-host
export REDIS_HOST=your-redis-host
export AI_PROVIDER=groq
export GROQ_API_KEY=your-production-key
```

#### 2. Docker Production Build
```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Deploy to production
docker-compose -f docker-compose.prod.yml up -d

# Health check
docker-compose -f docker-compose.prod.yml ps
```

### Kubernetes Deployment

#### 1. Helm Chart Structure
```
📁 infrastructure/kubernetes/helm-charts/restaurant-ai/
├── 📄 Chart.yaml
├── 📄 values.yaml
├── 📄 values.prod.yaml
├── 📁 templates/
│   ├── 📄 deployment.yaml
│   ├── 📄 service.yaml
│   ├── 📄 ingress.yaml
│   ├── 📄 configmap.yaml
│   ├── 📄 secret.yaml
│   └── 📄 hpa.yaml
└── 📁 charts/
    ├── 📁 postgresql/
    ├── 📁 redis/
    └── 📁 nginx-ingress/
```

#### 2. Deploy to Kubernetes
```bash
# Add Helm repositories
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

# Install dependencies
helm dependency update infrastructure/kubernetes/helm-charts/restaurant-ai/

# Deploy to staging
helm install restaurant-ai-staging \
  ./infrastructure/kubernetes/helm-charts/restaurant-ai/ \
  --namespace staging \
  --create-namespace \
  --values infrastructure/kubernetes/helm-charts/restaurant-ai/values.yaml

# Deploy to production
helm install restaurant-ai-prod \
  ./infrastructure/kubernetes/helm-charts/restaurant-ai/ \
  --namespace production \
  --create-namespace \
  --values infrastructure/kubernetes/helm-charts/restaurant-ai/values.prod.yaml
```

### AWS EKS Deployment
```bash
# Create EKS cluster
eksctl create cluster \
  --name restaurant-ai-cluster \
  --region us-west-2 \
  --nodes 3 \
  --node-type t3.medium \
  --with-oidc \
  --managed

# Configure kubectl
aws eks update-kubeconfig --region us-west-2 --name restaurant-ai-cluster

# Deploy application
helm install restaurant-ai \
  ./infrastructure/kubernetes/helm-charts/restaurant-ai/ \
  --namespace production \
  --create-namespace \
  --set ingress.enabled=true \
  --set ingress.className=alb \
  --set database.external.enabled=true \
  --set database.external.host=your-rds-endpoint
```

## 📚 API Documentation

### Restaurant Service API (`/api/v1/restaurants`)

#### Core Endpoints
```http
GET    /api/v1/restaurants                    # List all restaurants
POST   /api/v1/restaurants                    # Create restaurant
GET    /api/v1/restaurants/{slug}             # Get restaurant by slug
PUT    /api/v1/restaurants/{slug}             # Update restaurant
DELETE /api/v1/restaurants/{slug}             # Delete restaurant
GET    /api/v1/restaurants/{slug}/menu        # Get restaurant menu
GET    /api/v1/restaurants/{slug}/avatar      # Get AI avatar config
PUT    /api/v1/restaurants/{slug}/avatar      # Update avatar config
```

#### Example API Usage
```python
# Get restaurant with menu
import httpx

async def get_restaurant_data(slug: str):
    async with httpx.AsyncClient() as client:
        # Get restaurant info
        restaurant_response = await client.get(f"/api/v1/restaurants/{slug}")
        restaurant = restaurant_response.json()
        
        # Get menu data
        menu_response = await client.get(f"/api/v1/restaurants/{slug}/menu")
        menu = menu_response.json()
        
        # Get avatar configuration
        avatar_response = await client.get(f"/api/v1/restaurants/{slug}/avatar")
        avatar = avatar_response.json()
        
        return {
            "restaurant": restaurant,
            "menu": menu,
            "avatar": avatar
        }
```

### Menu Service API (`/api/v1/menu`)

#### Menu Management
```http
GET    /api/v1/menu/categories/{restaurant_id}     # Get menu categories
POST   /api/v1/menu/categories                     # Create category
PUT    /api/v1/menu/categories/{category_id}       # Update category
DELETE /api/v1/menu/categories/{category_id}       # Delete category

GET    /api/v1/menu/items/{restaurant_id}          # Get menu items
POST   /api/v1/menu/items                          # Create menu item
PUT    /api/v1/menu/items/{item_id}                # Update menu item
DELETE /api/v1/menu/items/{item_id}                # Delete menu item

GET    /api/v1/menu/ingredients/{restaurant_id}    # Get ingredients
POST   /api/v1/menu/ingredients                    # Create ingredient
PUT    /api/v1/menu/ingredients/{ingredient_id}    # Update ingredient
DELETE /api/v1/menu/ingredients/{ingredient_id}    # Delete ingredient
```

### AI Service API (`/api/v1/chat`)

#### Chat Endpoints
```http
POST   /api/v1/chat/{restaurant_slug}/message      # Send chat message
GET    /api/v1/chat/{restaurant_slug}/suggestions  # Get conversation starters
POST   /api/v1/chat/{restaurant_slug}/feedback     # Submit feedback
GET    /api/v1/chat/{restaurant_slug}/analytics    # Get chat analytics
```

#### WebSocket Chat
```javascript
// Frontend WebSocket integration
const socket = new WebSocket(`ws://localhost:8003/ws/${restaurantSlug}`);

socket.onmessage = function(event) {
    const message = JSON.parse(event.data);
    console.log('Received:', message);
};

socket.send(JSON.stringify({
    type: 'chat_message',
    message: 'Tell me about your signature cookies',
    session_id: 'user-session-123'
}));
```

## 🔒 Security

### Authentication & Authorization
```python
# JWT-based authentication
from jose import JWTError, jwt
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer

security = HTTPBearer()

async def get_current_user(token: str = Depends(security)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # Get user from database
    user = await get_user_by_id(user_id)
    if user is None:
        raise credentials_exception
    return user
```

### Rate Limiting
```python
# Redis-based rate limiting
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/v1/chat/{restaurant_slug}/message")
@limiter.limit("10/minute")  # 10 messages per minute per IP
async def send_message(request: Request, restaurant_slug: str, message: ChatMessage):
    # Handle chat message
    pass
```

### Input Validation & Sanitization
```python
# Pydantic schemas for input validation
from pydantic import BaseModel, validator, Field
from typing import Optional, List

class MenuItemCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    price: float = Field(..., gt=0, le=1000)
    allergen_info: Optional[List[str]] = Field(default_factory=list)
    
    @validator('name')
    def validate_name(cls, v):
        # Sanitize HTML and prevent XSS
        return bleach.clean(v.strip())
    
    @validator('description')
    def validate_description(cls, v):
        if v:
            return bleach.clean(v.strip())
        return v
```

### CORS Configuration
```python
# FastAPI CORS middleware
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
    expose_headers=["X-Total-Count"]
)
```

## 📊 Monitoring & Analytics

### Prometheus Metrics
```python
# Custom metrics collection
from prometheus_client import Counter, Histogram, Gauge
import time

# Define metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration')
ACTIVE_CONVERSATIONS = Gauge('active_conversations_total', 'Active chat conversations')

# Middleware for metrics collection
@app.middleware("http")
async def add_prometheus_metrics(request: Request, call_next):
    start_time = time.time()
    
    response = await call_next(request)
    
    # Record metrics
    REQUEST_COUNT.labels(method=request.method, endpoint=request.url.path).inc()
    REQUEST_DURATION.observe(time.time() - start_time)
    
    return response
```

### Health Checks
```python
# Health check endpoints
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

@app.get("/health/detailed")
async def detailed_health_check():
    return {
        "status": "healthy",
        "checks": {
            "database": await check_database_connection(),
            "redis": await check_redis_connection(),
            "ai_service": await check_ai_service(),
        }
    }
```

## 🌐 Scaling & Performance

### Horizontal Scaling
```yaml
# Kubernetes Horizontal Pod Autoscaler
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: restaurant-service-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: restaurant-service
  minReplicas: 3
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### Database Optimization
```python
# Connection pooling and query optimization
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True,
    echo=False
)

# Query optimization with eager loading
def get_restaurant_with_menu(restaurant_id: str):
    return session.query(Restaurant)\
        .options(
            joinedload(Restaurant.menu_categories)
            .joinedload(MenuCategory.menu_items)
        )\
        .filter(Restaurant.id == restaurant_id)\
        .first()
```

### Caching Strategy
```python
# Redis caching with TTL
import redis
import json
from functools import wraps

redis_client = redis.Redis(host='redis', port=6379, decode_responses=True)

def cache_result(ttl: int = 3600):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Create cache key
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Try to get from cache
            cached_result = redis_client.get(cache_key)
            if cached_result:
                return json.loads(cached_result)
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            redis_client.setex(cache_key, ttl, json.dumps(result, default=str))
            
            return result
        return wrapper
    return decorator

@cache_result(ttl=1800)  # Cache for 30 minutes
async def get_restaurant_menu(restaurant_id: str):
    # Expensive database query
    return await fetch_menu_from_database(restaurant_id)
```

## 🧪 Testing

### Testing Strategy
```python
# pytest configuration and fixtures
import pytest
import asyncio
from httpx import AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Test database setup
@pytest.fixture(scope="session")
def test_database():
    engine = create_engine("postgresql://test:test@localhost/test_db")
    TestSessionLocal = sessionmaker(bind=engine)
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    yield TestSessionLocal
    
    # Cleanup
    Base.metadata.drop_all(bind=engine)

# API client fixture
@pytest.fixture
async def async_client():
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

# Integration test example
@pytest.mark.asyncio
async def test_create_restaurant(async_client: AsyncClient, test_database):
    restaurant_data = {
        "name": "Test Restaurant",
        "slug": "test-restaurant",
        "cuisine_type": "Italian",
        "description": "A test restaurant"
    }
    
    response = await async_client.post("/api/v1/restaurants", json=restaurant_data)
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == restaurant_data["name"]
    assert data["slug"] == restaurant_data["slug"]
```

### End-to-End Testing with Playwright
```python
# E2E test for chat functionality
from playwright.async_api import async_playwright
import pytest

@pytest.mark.asyncio
async def test_ai_chat_flow():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        # Navigate to restaurant page
        await page.goto("http://localhost:3000/r/the-cookie-jar")
        
        # Open AI chat
        await page.click('[data-testid="ai-chat-button"]')
        
        # Send message
        await page.fill('[data-testid="chat-input"]', "Tell me about your cookies")
        await page.click('[data-testid="send-button"]')
        
        # Wait for AI response
        await page.wait_for_selector('[data-testid="ai-message"]')
        
        # Verify response
        ai_message = await page.text_content('[data-testid="ai-message"]')
        assert "cookie" in ai_message.lower()
        
        await browser.close()
```

## 🤝 Contributing

### Development Workflow
1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Install pre-commit hooks**: `pre-commit install`
4. **Make your changes**
5. **Run tests**: `pytest backend/tests/ && npm test`
6. **Commit changes**: `git commit -m "feat: add amazing feature"`
7. **Push to branch**: `git push origin feature/amazing-feature`
8. **Open a Pull Request**

### Code Standards
- **Python**: Follow PEP 8, use Black for formatting, Pylint for linting
- **TypeScript**: Follow ESLint configuration, use Prettier for formatting
- **Commits**: Use conventional commits format
- **Tests**: Maintain >80% code coverage
- **Documentation**: Update docs for any public API changes

### Pre-commit Hooks
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files

  - repo: https://github.com/psf/black
    rev: 23.1.0
    hooks:
      - id: black
        language_version: python3.11

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
        args: ["--profile", "black"]

  - repo: https://github.com/eslint/eslint
    rev: v8.36.0
    hooks:
      - id: eslint
        files: \.(js|ts|tsx)$
        types: [file]
```

## 📈 Enterprise Scalability

This platform is designed for enterprise-scale deployment:

### Multi-Tenant Architecture
- **Tenant Isolation**: Database-level tenant separation
- **Custom Domains**: Support for custom restaurant domains
- **White-Label Solutions**: Customizable branding and themes
- **Resource Quotas**: Per-tenant resource limits and monitoring

### Global Deployment
- **Multi-Region Support**: Deploy across multiple AWS/Azure regions
- **CDN Integration**: CloudFront/Azure CDN for global content delivery
- **Database Replication**: Read replicas for global performance
- **Localization**: Multi-language and multi-currency support

### Integration Capabilities
- **POS Systems**: Integration with Square, Toast, Clover
- **Payment Processors**: Stripe, PayPal, Square payments
- **Delivery Platforms**: DoorDash, Uber Eats, Grubhub APIs
- **Analytics**: Google Analytics, Mixpanel, Segment integration
- **CRM Systems**: Salesforce, HubSpot integration

## 📞 Support & Documentation

- **API Documentation**: [Swagger UI](http://localhost:8001/docs)
- **System Architecture**: [docs/ARCHITECTURE.md](./docs/ARCHITECTURE.md)
- **Deployment Guide**: [docs/DEPLOYMENT.md](./docs/DEPLOYMENT.md)
- **Security Guide**: [docs/SECURITY.md](./docs/SECURITY.md)
- **Contributing Guide**: [docs/CONTRIBUTING.md](./docs/CONTRIBUTING.md)
- **Issue Tracker**: [GitHub Issues](https://github.com/your-org/restaurant-ai-platform/issues)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Built with ❤️ for the restaurant industry**

*Empowering restaurants with AI-driven customer experiences*