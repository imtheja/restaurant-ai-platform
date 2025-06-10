# API Documentation

> Comprehensive API reference for the Restaurant AI Platform microservices

## Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Restaurant Service API](#restaurant-service-api)
4. [Menu Service API](#menu-service-api)
5. [AI Service API](#ai-service-api)
6. [WebSocket API](#websocket-api)
7. [Error Handling](#error-handling)
8. [Rate Limiting](#rate-limiting)
9. [SDK and Client Libraries](#sdk-and-client-libraries)

## Overview

The Restaurant AI Platform provides RESTful APIs across three core microservices:

- **Restaurant Service** (Port 8001): Restaurant management and configuration
- **Menu Service** (Port 8002): Menu items, categories, and ingredients
- **AI Service** (Port 8003): Conversational AI and chat functionality

All APIs follow REST conventions and return JSON responses. The APIs are documented using OpenAPI 3.0 and include interactive Swagger UI documentation.

### Base URLs
- **Development**: `http://localhost`
- **Production**: `https://your-domain.com`
- **API Gateway**: All requests route through Nginx reverse proxy

### API Versioning
All APIs use URL versioning with the prefix `/api/v1/`.

### Content Types
- **Request**: `application/json`
- **Response**: `application/json`
- **File Upload**: `multipart/form-data`

## Authentication

### JWT Authentication
```http
Authorization: Bearer <jwt_token>
```

### API Key Authentication (Optional)
```http
X-API-Key: <your_api_key>
```

### Obtaining JWT Tokens
```bash
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "secure_password"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600,
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

## Restaurant Service API

### Base URL: `/api/v1/restaurants`

#### List Restaurants
```http
GET /api/v1/restaurants
```

**Query Parameters:**
- `page` (integer): Page number (default: 1)
- `limit` (integer): Items per page (default: 20, max: 100)
- `cuisine_type` (string): Filter by cuisine type
- `is_active` (boolean): Filter by active status

**Response:**
```json
{
  "data": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "The Cookie Jar",
      "slug": "the-cookie-jar",
      "cuisine_type": "Cookies",
      "description": "Artisanal cookies and sweet treats",
      "is_active": true,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z",
      "avatar_config": {
        "name": "Baker Betty",
        "personality": "friendly_knowledgeable",
        "greeting": "Welcome to The Cookie Jar!"
      }
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 45,
    "pages": 3
  }
}
```

#### Create Restaurant
```http
POST /api/v1/restaurants
Content-Type: application/json
Authorization: Bearer <jwt_token>
```

**Request Body:**
```json
{
  "name": "Mario's Italian",
  "slug": "marios-italian",
  "cuisine_type": "Italian",
  "description": "Authentic Italian cuisine",
  "avatar_config": {
    "name": "Chef Mario",
    "personality": "warm_professional",
    "greeting": "Benvenuto! Welcome to Mario's Italian!"
  }
}
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440001",
  "name": "Mario's Italian",
  "slug": "marios-italian",
  "cuisine_type": "Italian",
  "description": "Authentic Italian cuisine",
  "is_active": true,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z",
  "avatar_config": {
    "name": "Chef Mario",
    "personality": "warm_professional",
    "greeting": "Benvenuto! Welcome to Mario's Italian!"
  }
}
```

#### Get Restaurant by Slug
```http
GET /api/v1/restaurants/{slug}
```

**Path Parameters:**
- `slug` (string): Restaurant slug identifier

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "The Cookie Jar",
  "slug": "the-cookie-jar",
  "cuisine_type": "Cookies",
  "description": "Artisanal cookies and sweet treats",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z",
  "avatar_config": {
    "name": "Baker Betty",
    "personality": "friendly_knowledgeable",
    "greeting": "Welcome to The Cookie Jar!",
    "tone": "warm",
    "special_instructions": "Always mention fresh-baked cookies"
  },
  "metadata": {
    "address": "123 Cookie Street",
    "phone": "+1-555-COOKIE",
    "hours": {
      "monday": "8:00-20:00",
      "tuesday": "8:00-20:00",
      "closed": ["sunday"]
    }
  }
}
```

#### Update Restaurant
```http
PUT /api/v1/restaurants/{slug}
Content-Type: application/json
Authorization: Bearer <jwt_token>
```

#### Delete Restaurant
```http
DELETE /api/v1/restaurants/{slug}
Authorization: Bearer <jwt_token>
```

#### Get Restaurant Menu
```http
GET /api/v1/restaurants/{slug}/menu
```

**Response:**
```json
{
  "restaurant_id": "550e8400-e29b-41d4-a716-446655440000",
  "categories": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440010",
      "name": "Signature Cookies",
      "description": "Our most popular cookie creations",
      "display_order": 1,
      "items": [
        {
          "id": "550e8400-e29b-41d4-a716-446655440100",
          "name": "Baker Betty's OG",
          "description": "Our original chocolate chip cookie recipe",
          "price": 3.50,
          "image_url": "https://example.com/images/og-cookie.jpg",
          "is_signature": true,
          "spice_level": 0,
          "allergen_info": ["gluten", "dairy", "eggs"],
          "tags": ["popular", "classic"],
          "display_order": 1,
          "is_available": true,
          "created_at": "2024-01-01T00:00:00Z",
          "updated_at": "2024-01-15T10:30:00Z"
        }
      ]
    }
  ]
}
```

#### Get Avatar Configuration
```http
GET /api/v1/restaurants/{slug}/avatar
```

#### Update Avatar Configuration
```http
PUT /api/v1/restaurants/{slug}/avatar
Content-Type: application/json
Authorization: Bearer <jwt_token>
```

## Menu Service API

### Base URL: `/api/v1/menu`

#### Categories

##### List Categories
```http
GET /api/v1/menu/categories/{restaurant_id}
```

**Response:**
```json
{
  "data": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440010",
      "restaurant_id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "Signature Cookies",
      "description": "Our most popular cookie creations",
      "display_order": 1,
      "is_active": true,
      "created_at": "2024-01-01T00:00:00Z",
      "item_count": 5
    }
  ]
}
```

##### Create Category
```http
POST /api/v1/menu/categories
Content-Type: application/json
Authorization: Bearer <jwt_token>
```

**Request Body:**
```json
{
  "restaurant_id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Specialty Cookies",
  "description": "Limited edition and seasonal cookies",
  "display_order": 2
}
```

##### Update Category
```http
PUT /api/v1/menu/categories/{category_id}
Content-Type: application/json
Authorization: Bearer <jwt_token>
```

##### Delete Category
```http
DELETE /api/v1/menu/categories/{category_id}
Authorization: Bearer <jwt_token>
```

#### Menu Items

##### List Menu Items
```http
GET /api/v1/menu/items/{restaurant_id}
```

**Query Parameters:**
- `category_id` (string): Filter by category
- `is_available` (boolean): Filter by availability
- `is_signature` (boolean): Filter signature items
- `search` (string): Search by name or description

**Response:**
```json
{
  "data": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440100",
      "restaurant_id": "550e8400-e29b-41d4-a716-446655440000",
      "category_id": "550e8400-e29b-41d4-a716-446655440010",
      "name": "Baker Betty's OG",
      "description": "Our original chocolate chip cookie recipe with premium Belgian chocolate",
      "price": 3.50,
      "image_url": "https://example.com/images/og-cookie.jpg",
      "is_signature": true,
      "spice_level": 0,
      "allergen_info": ["gluten", "dairy", "eggs"],
      "tags": ["popular", "classic", "bestseller"],
      "display_order": 1,
      "is_available": true,
      "nutritional_info": {
        "calories": 320,
        "protein": 4,
        "carbs": 42,
        "fat": 16,
        "fiber": 2
      },
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 15,
    "pages": 1
  }
}
```

##### Create Menu Item
```http
POST /api/v1/menu/items
Content-Type: application/json
Authorization: Bearer <jwt_token>
```

**Request Body:**
```json
{
  "restaurant_id": "550e8400-e29b-41d4-a716-446655440000",
  "category_id": "550e8400-e29b-41d4-a716-446655440010",
  "name": "Double Chocolate Delight",
  "description": "Rich chocolate cookie with dark chocolate chunks",
  "price": 4.25,
  "is_signature": false,
  "spice_level": 0,
  "allergen_info": ["gluten", "dairy"],
  "tags": ["chocolate", "rich"],
  "display_order": 10,
  "nutritional_info": {
    "calories": 380,
    "protein": 5,
    "carbs": 48,
    "fat": 20
  }
}
```

##### Update Menu Item
```http
PUT /api/v1/menu/items/{item_id}
Content-Type: application/json
Authorization: Bearer <jwt_token>
```

##### Delete Menu Item
```http
DELETE /api/v1/menu/items/{item_id}
Authorization: Bearer <jwt_token>
```

##### Upload Menu Item Image
```http
POST /api/v1/menu/items/{item_id}/image
Content-Type: multipart/form-data
Authorization: Bearer <jwt_token>
```

**Form Data:**
- `image` (file): Image file (max 5MB, JPEG/PNG)

#### Ingredients

##### List Ingredients
```http
GET /api/v1/menu/ingredients/{restaurant_id}
```

##### Create Ingredient
```http
POST /api/v1/menu/ingredients
Content-Type: application/json
Authorization: Bearer <jwt_token>
```

**Request Body:**
```json
{
  "restaurant_id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Belgian Dark Chocolate",
  "description": "Premium 70% cocoa dark chocolate chunks",
  "allergen_info": ["dairy"],
  "supplier_info": {
    "supplier": "Callebaut",
    "product_code": "CHD-70-1KG"
  }
}
```

## AI Service API

### Base URL: `/api/v1/chat`

#### Send Chat Message
```http
POST /api/v1/chat/{restaurant_slug}/message
Content-Type: application/json
```

**Request Body:**
```json
{
  "message": "Tell me about your signature cookies",
  "session_id": "session-1234567890",
  "context": {
    "source": "voice_chat",
    "user_preferences": {
      "dietary_restrictions": ["gluten-free"],
      "favorite_flavors": ["chocolate", "vanilla"]
    }
  }
}
```

**Response:**
```json
{
  "message": "Oh, you'll love our signature cookies! Baker Betty's OG is our most popular - it's our original chocolate chip recipe with premium Belgian chocolate. Want to try it with some cream cheese frosting for just $1 more?",
  "suggestions": [
    "Tell me about Baker Betty's OG",
    "What cookies are gluten-free?",
    "Show me today's specials"
  ],
  "recommendations": [
    {
      "item_id": "550e8400-e29b-41d4-a716-446655440100",
      "name": "Baker Betty's OG",
      "reason": "Most popular signature cookie",
      "upsell": "Add cream cheese frosting (+$1.00)"
    }
  ],
  "conversation_id": "550e8400-e29b-41d4-a716-446655440200",
  "message_id": "550e8400-e29b-41d4-a716-446655440300",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### Get Conversation Suggestions
```http
GET /api/v1/chat/{restaurant_slug}/suggestions
```

**Query Parameters:**
- `context` (string): Context for suggestions (e.g., "menu_browsing", "ordering")

**Response:**
```json
{
  "suggestions": [
    "What are your most popular cookies?",
    "Do you have any gluten-free options?",
    "Tell me about Baker Betty's OG",
    "What's fresh out of the oven today?",
    "Can you recommend something sweet but not too rich?"
  ]
}
```

#### Submit Chat Feedback
```http
POST /api/v1/chat/{restaurant_slug}/feedback
Content-Type: application/json
```

**Request Body:**
```json
{
  "conversation_id": "550e8400-e29b-41d4-a716-446655440200",
  "message_id": "550e8400-e29b-41d4-a716-446655440300",
  "rating": 5,
  "feedback_type": "helpful",
  "comment": "Great recommendations! The AI understood my dietary restrictions.",
  "sentiment": "positive"
}
```

#### Get Chat Analytics
```http
GET /api/v1/chat/{restaurant_slug}/analytics
Authorization: Bearer <jwt_token>
```

**Query Parameters:**
- `days` (integer): Number of days (default: 7, max: 365)
- `metrics` (array): Specific metrics to include

**Response:**
```json
{
  "period": {
    "start_date": "2024-01-08T00:00:00Z",
    "end_date": "2024-01-15T00:00:00Z",
    "days": 7
  },
  "metrics": {
    "total_conversations": 150,
    "total_messages": 875,
    "avg_conversation_length": 5.8,
    "avg_response_time_ms": 1200,
    "customer_satisfaction": 4.6,
    "conversion_rate": 0.32
  },
  "top_topics": [
    {
      "topic": "signature_cookies",
      "count": 45,
      "percentage": 30.0
    },
    {
      "topic": "allergen_info",
      "count": 38,
      "percentage": 25.3
    }
  ],
  "popular_questions": [
    "What are your signature cookies?",
    "Do you have gluten-free options?",
    "What's the most popular cookie?"
  ]
}
```

## WebSocket API

### Connection
```javascript
// Connect to WebSocket
const socket = new WebSocket('ws://localhost:8003/ws/{restaurant_slug}');

// Authentication via query parameter or subprotocol
const socket = new WebSocket('ws://localhost:8003/ws/{restaurant_slug}?token={jwt_token}');
```

### Message Format
All WebSocket messages use JSON format:

```json
{
  "type": "message_type",
  "data": { /* message payload */ },
  "timestamp": "2024-01-15T10:30:00Z",
  "id": "message_id"
}
```

### Message Types

#### Chat Message
```json
{
  "type": "chat_message",
  "data": {
    "message": "Tell me about your cookies",
    "session_id": "session-123",
    "context": {
      "source": "websocket"
    }
  }
}
```

#### AI Response
```json
{
  "type": "ai_response",
  "data": {
    "message": "We have amazing signature cookies!",
    "suggestions": ["Tell me more", "Show me prices"],
    "recommendations": [...]
  }
}
```

#### Typing Indicator
```json
{
  "type": "typing",
  "data": {
    "is_typing": true,
    "sender": "ai"
  }
}
```

#### Real-time Menu Updates
```json
{
  "type": "menu_update",
  "data": {
    "item_id": "550e8400-e29b-41d4-a716-446655440100",
    "change_type": "availability",
    "is_available": false,
    "reason": "sold_out"
  }
}
```

## Error Handling

### Error Response Format
```json
{
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "Restaurant not found",
    "details": "No restaurant found with slug 'invalid-slug'",
    "timestamp": "2024-01-15T10:30:00Z",
    "request_id": "req-550e8400-e29b-41d4-a716-446655440999"
  }
}
```

### HTTP Status Codes

| Code | Status | Description |
|------|--------|-------------|
| 200 | OK | Request successful |
| 201 | Created | Resource created successfully |
| 400 | Bad Request | Invalid request parameters |
| 401 | Unauthorized | Authentication required |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 409 | Conflict | Resource already exists |
| 422 | Unprocessable Entity | Validation error |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |
| 503 | Service Unavailable | Service temporarily unavailable |

### Error Codes

| Code | Description |
|------|-------------|
| `VALIDATION_ERROR` | Request validation failed |
| `RESOURCE_NOT_FOUND` | Requested resource not found |
| `DUPLICATE_RESOURCE` | Resource already exists |
| `AUTHENTICATION_REQUIRED` | Valid authentication required |
| `INSUFFICIENT_PERMISSIONS` | User lacks required permissions |
| `RATE_LIMIT_EXCEEDED` | API rate limit exceeded |
| `AI_SERVICE_UNAVAILABLE` | AI service temporarily unavailable |
| `DATABASE_ERROR` | Database operation failed |

## Rate Limiting

### Rate Limits by Endpoint

| Endpoint | Limit | Window |
|----------|-------|--------|
| `/api/v1/chat/*/message` | 10 requests | 1 minute |
| `/api/v1/restaurants` (GET) | 100 requests | 1 minute |
| `/api/v1/restaurants` (POST/PUT/DELETE) | 20 requests | 1 minute |
| `/api/v1/menu/*` | 50 requests | 1 minute |
| All other endpoints | 200 requests | 1 minute |

### Rate Limit Headers
```http
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 7
X-RateLimit-Reset: 1642248000
Retry-After: 60
```

## SDK and Client Libraries

### JavaScript/TypeScript SDK
```bash
npm install @restaurant-ai/sdk
```

```typescript
import { RestaurantAIClient } from '@restaurant-ai/sdk';

const client = new RestaurantAIClient({
  baseUrl: 'https://api.restaurant-ai.com',
  apiKey: 'your_api_key'
});

// Get restaurant data
const restaurant = await client.restaurants.get('the-cookie-jar');

// Send chat message
const response = await client.chat.sendMessage('the-cookie-jar', {
  message: 'What cookies do you recommend?',
  sessionId: 'session-123'
});
```

### Python SDK
```bash
pip install restaurant-ai-sdk
```

```python
from restaurant_ai import RestaurantAIClient

client = RestaurantAIClient(
    base_url='https://api.restaurant-ai.com',
    api_key='your_api_key'
)

# Get restaurant data
restaurant = client.restaurants.get('the-cookie-jar')

# Send chat message
response = client.chat.send_message(
    restaurant_slug='the-cookie-jar',
    message='What cookies do you recommend?',
    session_id='session-123'
)
```

### cURL Examples

#### Get Restaurant
```bash
curl -X GET \
  'http://localhost:8001/api/v1/restaurants/the-cookie-jar' \
  -H 'Accept: application/json'
```

#### Send Chat Message
```bash
curl -X POST \
  'http://localhost:8003/api/v1/chat/the-cookie-jar/message' \
  -H 'Content-Type: application/json' \
  -d '{
    "message": "Tell me about your signature cookies",
    "session_id": "session-123"
  }'
```

#### Create Menu Item
```bash
curl -X POST \
  'http://localhost:8002/api/v1/menu/items' \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer your_jwt_token' \
  -d '{
    "restaurant_id": "550e8400-e29b-41d4-a716-446655440000",
    "category_id": "550e8400-e29b-41d4-a716-446655440010",
    "name": "New Cookie",
    "description": "A delicious new cookie",
    "price": 3.75
  }'
```

## Testing

### API Testing with Postman
Import the Postman collection from `/docs/postman/Restaurant-AI-Platform.postman_collection.json`

### Integration Testing
```bash
# Run API integration tests
pytest tests/api/

# Run specific service tests
pytest tests/api/test_restaurant_service.py
pytest tests/api/test_menu_service.py
pytest tests/api/test_ai_service.py
```

### Load Testing
```bash
# Install artillery
npm install -g artillery

# Run load tests
artillery run tests/load/api-load-test.yml
```

---

For more information, visit the [Interactive API Documentation](http://localhost:8001/docs) or contact our support team.