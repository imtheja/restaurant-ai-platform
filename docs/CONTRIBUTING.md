# Contributing Guide

> Welcome to the Restaurant AI Platform! This guide will help you get started with contributing to this open-source project.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Development Setup](#development-setup)
3. [Development Workflow](#development-workflow)
4. [Coding Standards](#coding-standards)
5. [Testing Guidelines](#testing-guidelines)
6. [Documentation](#documentation)
7. [Pull Request Process](#pull-request-process)
8. [Issue Guidelines](#issue-guidelines)
9. [Community Guidelines](#community-guidelines)
10. [Recognition](#recognition)

## Getting Started

### Ways to Contribute

We welcome all types of contributions:

- 🐛 **Bug Reports**: Help us identify and fix issues
- ✨ **Feature Requests**: Suggest new functionality
- 💻 **Code Contributions**: Implement features, fix bugs, improve performance
- 📚 **Documentation**: Improve guides, API docs, and tutorials
- 🎨 **Design**: UI/UX improvements and design assets
- 🌍 **Translations**: Help make the platform accessible globally
- 🧪 **Testing**: Add test cases and improve test coverage
- 📢 **Community**: Help others in discussions and forums

### Project Overview

The Restaurant AI Platform is built with:
- **Backend**: Python 3.11+, FastAPI, PostgreSQL, Redis
- **Frontend**: React 18+, TypeScript, Material-UI, Vite
- **AI**: OpenAI/Groq integration, speech recognition
- **Infrastructure**: Docker, Kubernetes, Nginx
- **Monitoring**: Prometheus, Grafana, ELK Stack

### Code of Conduct

This project adheres to a [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you agree to uphold this code. Please report unacceptable behavior to [conduct@restaurant-ai.com](mailto:conduct@restaurant-ai.com).

## Development Setup

### Prerequisites

```bash
# Required
Docker Desktop 4.0+
Node.js 18+
Python 3.11+
Git 2.30+

# Recommended
VS Code with extensions:
- Python
- TypeScript
- Docker
- GitLens
- Prettier
- ESLint
```

### Initial Setup

1. **Fork the Repository**
   ```bash
   # Click "Fork" on GitHub, then clone your fork
   git clone https://github.com/YOUR_USERNAME/restaurant-ai-platform.git
   cd restaurant-ai-platform
   
   # Add upstream remote
   git remote add upstream https://github.com/restaurant-ai/restaurant-ai-platform.git
   ```

2. **Environment Setup**
   ```bash
   # Copy environment files
   cp .env.example .env
   cp frontend/.env.example frontend/.env
   
   # Edit .env with your configuration
   # At minimum, set AI_PROVIDER=groq and add your GROQ_API_KEY
   ```

3. **Install Dependencies**
   ```bash
   # Backend dependencies
   cd backend
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   
   # Frontend dependencies
   cd ../frontend
   npm install
   
   # Install pre-commit hooks
   cd ..
   pip install pre-commit
   pre-commit install
   ```

4. **Start Development Environment**
   ```bash
   # Start infrastructure
   docker-compose up -d postgres redis
   
   # Initialize database
   python scripts/init_db.py
   python scripts/load_cookie_shop.py
   
   # Start all services
   npm run dev:all
   ```

5. **Verify Setup**
   ```bash
   # Check that all services are running
   curl http://localhost:8001/health  # Restaurant service
   curl http://localhost:8002/health  # Menu service  
   curl http://localhost:8003/health  # AI service
   curl http://localhost:3000         # Frontend
   ```

### Development Scripts

```bash
# Development commands
npm run dev:all              # Start all services
npm run dev:backend          # Start backend services only
npm run dev:frontend         # Start frontend only

# Testing commands
npm run test                 # Run all tests
npm run test:backend         # Backend tests only
npm run test:frontend        # Frontend tests only
npm run test:e2e             # End-to-end tests
npm run test:watch           # Watch mode

# Code quality
npm run lint                 # Lint all code
npm run lint:fix             # Fix linting issues
npm run format               # Format code
npm run type-check           # TypeScript type checking

# Database commands
npm run db:migrate           # Run migrations
npm run db:seed              # Seed test data
npm run db:reset             # Reset database
npm run db:backup            # Backup database
```

## Development Workflow

### Git Workflow

We use the **Git Flow** branching model:

```
main branch (production-ready)
├── develop branch (integration)
    ├── feature/feature-name
    ├── bugfix/bug-description
    └── hotfix/critical-fix
```

### Creating a Feature

```bash
# Start from develop branch
git checkout develop
git pull upstream develop

# Create feature branch
git checkout -b feature/amazing-new-feature

# Make your changes
# ... code, test, commit ...

# Push to your fork
git push origin feature/amazing-new-feature

# Create Pull Request on GitHub
```

### Branch Naming Convention

- `feature/description` - New features
- `bugfix/issue-description` - Bug fixes
- `hotfix/critical-issue` - Critical production fixes
- `docs/topic` - Documentation updates
- `refactor/component-name` - Code refactoring
- `test/test-description` - Test improvements

### Commit Messages

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```bash
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Formatting, missing semicolons, etc.
- `refactor`: Code change that neither fixes bug nor adds feature
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```bash
feat(chat): add speech-to-text functionality
fix(menu): resolve category filtering issue
docs(api): update authentication examples
test(restaurant): add integration tests for CRUD operations
```

### Keeping Your Fork Updated

```bash
# Fetch upstream changes
git fetch upstream

# Update develop branch
git checkout develop
git merge upstream/develop
git push origin develop

# Rebase feature branch (if needed)
git checkout feature/your-feature
git rebase develop
```

## Coding Standards

### Python (Backend)

#### Style Guide
- Follow [PEP 8](https://pep8.org/)
- Use [Black](https://black.readthedocs.io/) for formatting
- Use [isort](https://pycqa.github.io/isort/) for import sorting
- Maximum line length: 88 characters (Black default)

#### Code Structure
```python
# File: backend/restaurant-service/routers/restaurants.py
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database.connection import get_db
from database.models import Restaurant
from schemas import RestaurantCreate, RestaurantResponse
from services.restaurant_service import RestaurantService

router = APIRouter(prefix="/api/v1/restaurants", tags=["restaurants"])

@router.get("/", response_model=List[RestaurantResponse])
async def list_restaurants(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    service: RestaurantService = Depends()
) -> List[RestaurantResponse]:
    """List all restaurants with pagination."""
    restaurants = await service.list_restaurants(db, skip=skip, limit=limit)
    return restaurants
```

#### Error Handling
```python
# Use specific exceptions
from fastapi import HTTPException, status

class RestaurantNotFoundError(Exception):
    """Raised when restaurant is not found."""
    pass

# In route handlers
try:
    restaurant = await service.get_restaurant(db, restaurant_id)
except RestaurantNotFoundError:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Restaurant with id {restaurant_id} not found"
    )
```

#### Async Best Practices
```python
# Use async/await consistently
async def get_restaurant_menu(restaurant_id: UUID) -> MenuResponse:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"/api/v1/menu/{restaurant_id}")
        return MenuResponse(**response.json())

# Use async context managers
async with database.transaction():
    restaurant = await create_restaurant(data)
    await create_default_menu(restaurant.id)
```

#### Type Hints
```python
from typing import List, Optional, Dict, Any, Union
from uuid import UUID
from datetime import datetime

# Function signatures
async def create_restaurant(
    data: RestaurantCreate,
    db: Session,
    current_user: User
) -> RestaurantResponse:
    pass

# Class definitions
@dataclass
class RestaurantData:
    name: str
    slug: str
    cuisine_type: Optional[str] = None
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
```

### TypeScript (Frontend)

#### Style Guide
- Use [ESLint](https://eslint.org/) with React/TypeScript config
- Use [Prettier](https://prettier.io/) for formatting
- Maximum line length: 100 characters
- Use semicolons and trailing commas

#### Component Structure
```typescript
// File: frontend/src/components/restaurant/RestaurantCard.tsx
import React from 'react';
import { Card, CardContent, Typography, Button } from '@mui/material';
import { Restaurant } from '@/types';

interface RestaurantCardProps {
  restaurant: Restaurant;
  onSelect: (id: string) => void;
  className?: string;
}

export const RestaurantCard: React.FC<RestaurantCardProps> = ({
  restaurant,
  onSelect,
  className
}) => {
  const handleClick = () => {
    onSelect(restaurant.id);
  };

  return (
    <Card className={className} onClick={handleClick}>
      <CardContent>
        <Typography variant="h6" component="h3">
          {restaurant.name}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          {restaurant.cuisine_type}
        </Typography>
        <Button variant="contained" color="primary">
          View Menu
        </Button>
      </CardContent>
    </Card>
  );
};

export default RestaurantCard;
```

#### Hooks and State Management
```typescript
// Custom hooks
import { useState, useEffect, useCallback } from 'react';
import { useQuery, useMutation } from 'react-query';

export const useRestaurant = (slug: string) => {
  const { data, isLoading, error } = useQuery(
    ['restaurant', slug],
    () => api.restaurants.get(slug),
    {
      enabled: !!slug,
      staleTime: 5 * 60 * 1000, // 5 minutes
    }
  );

  return { restaurant: data, isLoading, error };
};

// Component state
const [isOpen, setIsOpen] = useState(false);
const [selectedItem, setSelectedItem] = useState<MenuItem | null>(null);

const handleItemSelect = useCallback((item: MenuItem) => {
  setSelectedItem(item);
  setIsOpen(true);
}, []);
```

#### Error Boundaries
```typescript
// components/ErrorBoundary.tsx
import React, { Component, ErrorInfo, ReactNode } from 'react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Uncaught error:', error, errorInfo);
    // Send to error reporting service
  }

  public render() {
    if (this.state.hasError) {
      return this.props.fallback || <h1>Something went wrong.</h1>;
    }

    return this.props.children;
  }
}
```

### API Design

#### RESTful Conventions
```http
GET    /api/v1/restaurants           # List restaurants
POST   /api/v1/restaurants           # Create restaurant
GET    /api/v1/restaurants/{id}      # Get restaurant
PUT    /api/v1/restaurants/{id}      # Update restaurant
DELETE /api/v1/restaurants/{id}      # Delete restaurant

# Nested resources
GET    /api/v1/restaurants/{id}/menu # Get restaurant menu
POST   /api/v1/restaurants/{id}/menu # Create menu item
```

#### Response Format
```json
{
  "data": {
    "id": "uuid",
    "name": "Restaurant Name",
    "created_at": "2024-01-01T00:00:00Z"
  },
  "meta": {
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 100
    }
  }
}
```

#### Error Response Format
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input provided",
    "details": {
      "field": "email",
      "constraint": "Valid email address required"
    },
    "timestamp": "2024-01-01T00:00:00Z"
  }
}
```

## Testing Guidelines

### Testing Strategy

We follow the testing pyramid:
- **Unit Tests (70%)**: Test individual functions and components
- **Integration Tests (20%)**: Test service interactions
- **End-to-End Tests (10%)**: Test complete user workflows

### Backend Testing

#### Unit Tests with Pytest
```python
# tests/unit/test_restaurant_service.py
import pytest
from unittest.mock import Mock, AsyncMock
from uuid import uuid4

from services.restaurant_service import RestaurantService
from database.models import Restaurant
from schemas import RestaurantCreate

@pytest.fixture
def mock_db():
    return Mock()

@pytest.fixture
def restaurant_service():
    return RestaurantService()

@pytest.mark.asyncio
async def test_create_restaurant_success(restaurant_service, mock_db):
    # Arrange
    restaurant_data = RestaurantCreate(
        name="Test Restaurant",
        slug="test-restaurant",
        cuisine_type="Italian"
    )
    
    expected_restaurant = Restaurant(
        id=uuid4(),
        name=restaurant_data.name,
        slug=restaurant_data.slug,
        cuisine_type=restaurant_data.cuisine_type
    )
    
    mock_db.add = Mock()
    mock_db.commit = AsyncMock()
    mock_db.refresh = Mock()
    
    # Act
    result = await restaurant_service.create_restaurant(mock_db, restaurant_data)
    
    # Assert
    assert result.name == restaurant_data.name
    assert result.slug == restaurant_data.slug
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()

@pytest.mark.asyncio
async def test_create_restaurant_duplicate_slug(restaurant_service, mock_db):
    # Test duplicate slug handling
    pass
```

#### Integration Tests
```python
# tests/integration/test_restaurant_api.py
import pytest
from httpx import AsyncClient
from fastapi.testclient import TestClient

from main import app

@pytest.fixture
async def async_client():
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.mark.asyncio
async def test_create_restaurant_endpoint(async_client):
    restaurant_data = {
        "name": "Test Restaurant",
        "slug": "test-restaurant",
        "cuisine_type": "Italian"
    }
    
    response = await async_client.post("/api/v1/restaurants", json=restaurant_data)
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == restaurant_data["name"]
    assert "id" in data
```

### Frontend Testing

#### Component Tests with Jest and Testing Library
```typescript
// components/__tests__/RestaurantCard.test.tsx
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { RestaurantCard } from '../RestaurantCard';
import { Restaurant } from '@/types';

const mockRestaurant: Restaurant = {
  id: '1',
  name: 'Test Restaurant',
  slug: 'test-restaurant',
  cuisine_type: 'Italian',
  is_active: true
};

describe('RestaurantCard', () => {
  it('renders restaurant information correctly', () => {
    const mockOnSelect = jest.fn();
    
    render(
      <RestaurantCard 
        restaurant={mockRestaurant} 
        onSelect={mockOnSelect} 
      />
    );
    
    expect(screen.getByText('Test Restaurant')).toBeInTheDocument();
    expect(screen.getByText('Italian')).toBeInTheDocument();
  });
  
  it('calls onSelect when clicked', () => {
    const mockOnSelect = jest.fn();
    
    render(
      <RestaurantCard 
        restaurant={mockRestaurant} 
        onSelect={mockOnSelect} 
      />
    );
    
    fireEvent.click(screen.getByText('View Menu'));
    expect(mockOnSelect).toHaveBeenCalledWith('1');
  });
});
```

#### Hook Tests
```typescript
// hooks/__tests__/useRestaurant.test.ts
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from 'react-query';
import { useRestaurant } from '../useRestaurant';

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
    },
  });
  
  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
};

describe('useRestaurant', () => {
  it('fetches restaurant data successfully', async () => {
    const { result } = renderHook(
      () => useRestaurant('test-restaurant'),
      { wrapper: createWrapper() }
    );
    
    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });
    
    expect(result.current.restaurant).toBeDefined();
  });
});
```

### End-to-End Testing with Playwright

```typescript
// tests/e2e/restaurant-flow.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Restaurant Flow', () => {
  test('user can browse restaurant menu and chat with AI', async ({ page }) => {
    // Navigate to restaurant page
    await page.goto('/r/the-cookie-jar');
    
    // Verify restaurant header
    await expect(page.getByText('The Cookie Jar')).toBeVisible();
    
    // Verify menu items are displayed
    await expect(page.getByText("Baker Betty's OG")).toBeVisible();
    
    // Open AI chat
    await page.click('[data-testid="ai-chat-button"]');
    await expect(page.getByText('Baker Betty')).toBeVisible();
    
    // Send message to AI
    await page.fill('[data-testid="chat-input"]', 'Tell me about your cookies');
    await page.click('[data-testid="send-button"]');
    
    // Wait for AI response
    await expect(page.getByTestId('ai-message')).toBeVisible({ timeout: 10000 });
    
    // Verify response contains relevant information
    const aiResponse = await page.getByTestId('ai-message').textContent();
    expect(aiResponse).toContain('cookie');
  });
  
  test('user can filter menu items by category', async ({ page }) => {
    await page.goto('/r/the-cookie-jar');
    
    // Click on category filter
    await page.click('[data-testid="category-signature"]');
    
    // Verify only signature items are shown
    await expect(page.getByText("Baker Betty's OG")).toBeVisible();
    await expect(page.getByText('🌟 Signature')).toBeVisible();
  });
});
```

### Test Data Management

```python
# tests/fixtures/restaurant_fixtures.py
import pytest
from uuid import uuid4
from database.models import Restaurant, MenuCategory, MenuItem

@pytest.fixture
def sample_restaurant():
    return Restaurant(
        id=uuid4(),
        name="Test Restaurant",
        slug="test-restaurant",
        cuisine_type="Italian",
        is_active=True
    )

@pytest.fixture
def sample_menu_category(sample_restaurant):
    return MenuCategory(
        id=uuid4(),
        restaurant_id=sample_restaurant.id,
        name="Main Courses",
        display_order=1,
        is_active=True
    )

@pytest.fixture
def sample_menu_item(sample_restaurant, sample_menu_category):
    return MenuItem(
        id=uuid4(),
        restaurant_id=sample_restaurant.id,
        category_id=sample_menu_category.id,
        name="Margherita Pizza",
        description="Classic tomato and mozzarella",
        price=12.99,
        is_available=True
    )
```

## Documentation

### Code Documentation

#### Python Docstrings
```python
def create_restaurant(data: RestaurantCreate, db: Session) -> Restaurant:
    """Create a new restaurant.
    
    Args:
        data: Restaurant creation data containing name, slug, and cuisine type.
        db: Database session for executing queries.
        
    Returns:
        Restaurant: The created restaurant instance with generated ID.
        
    Raises:
        DuplicateSlugError: If a restaurant with the same slug already exists.
        ValidationError: If the provided data fails validation.
        
    Example:
        >>> restaurant_data = RestaurantCreate(
        ...     name="Mario's Pizza",
        ...     slug="marios-pizza",
        ...     cuisine_type="Italian"
        ... )
        >>> restaurant = create_restaurant(restaurant_data, db)
        >>> print(restaurant.name)
        "Mario's Pizza"
    """
    pass
```

#### TypeScript JSDoc
```typescript
/**
 * Hook for managing restaurant data and operations.
 * 
 * @param slug - The restaurant slug identifier
 * @returns Object containing restaurant data, loading state, and operations
 * 
 * @example
 * ```tsx
 * const { restaurant, isLoading, updateRestaurant } = useRestaurant('marios-pizza');
 * 
 * if (isLoading) return <Loading />;
 * 
 * return <RestaurantCard restaurant={restaurant} />;
 * ```
 */
export const useRestaurant = (slug: string) => {
  // Implementation
};
```

### API Documentation

Update OpenAPI schemas in FastAPI routes:

```python
@router.post(
    "/",
    response_model=RestaurantResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new restaurant",
    description="Create a new restaurant with the provided information.",
    responses={
        201: {"description": "Restaurant created successfully"},
        400: {"description": "Invalid input data"},
        409: {"description": "Restaurant with this slug already exists"}
    }
)
async def create_restaurant(
    restaurant: RestaurantCreate = Body(
        ...,
        example={
            "name": "Mario's Italian Restaurant",
            "slug": "marios-italian",
            "cuisine_type": "Italian",
            "description": "Authentic Italian cuisine in the heart of the city"
        }
    ),
    db: Session = Depends(get_db)
) -> RestaurantResponse:
    """Create a new restaurant."""
    pass
```

### README Updates

When adding new features, update the main README.md:

```markdown
## New Feature: Voice Ordering

The Restaurant AI Platform now supports voice-to-order functionality:

- **Speech Recognition**: Convert customer speech to text
- **Natural Language Processing**: Understand order intent
- **Order Confirmation**: Verbal confirmation of orders
- **Multi-language Support**: Support for 10+ languages

### Usage

```typescript
import { useVoiceOrdering } from '@/hooks/useVoiceOrdering';

const { startListening, stopListening, isListening, order } = useVoiceOrdering();
```

See [Voice Ordering Guide](docs/VOICE_ORDERING.md) for detailed implementation.
```

## Pull Request Process

### Before Submitting

1. **Test Your Changes**
   ```bash
   npm run test
   npm run test:e2e
   npm run lint
   npm run type-check
   ```

2. **Update Documentation**
   - Add/update docstrings and comments
   - Update API documentation if needed
   - Add/update tests
   - Update README if adding features

3. **Check Dependencies**
   ```bash
   # Check for security vulnerabilities
   npm audit
   pip-audit  # If available
   
   # Update requirements if needed
   pip freeze > requirements.txt
   ```

### Pull Request Template

```markdown
## Description
Brief description of changes made.

## Type of Change
- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] E2E tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows project coding standards
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests added for new functionality
- [ ] No new security vulnerabilities introduced

## Screenshots (if applicable)
Add screenshots for UI changes.

## Additional Notes
Any additional information or context.
```

### Review Process

1. **Automated Checks**: All CI checks must pass
2. **Code Review**: At least one maintainer review required
3. **Testing**: Feature must be tested in staging environment
4. **Documentation**: All changes must be documented

### Merging

- Use **Squash and Merge** for feature branches
- Use **Merge Commit** for release branches
- Delete feature branches after merging

## Issue Guidelines

### Bug Reports

Use the bug report template:

```markdown
**Bug Description**
A clear description of the bug.

**Steps to Reproduce**
1. Go to '...'
2. Click on '...'
3. See error

**Expected Behavior**
What you expected to happen.

**Actual Behavior**
What actually happened.

**Environment**
- OS: [e.g., macOS 13.0]
- Browser: [e.g., Chrome 110]
- Version: [e.g., 1.0.0]

**Additional Context**
Screenshots, logs, or other context.
```

### Feature Requests

Use the feature request template:

```markdown
**Feature Description**
A clear description of the feature.

**Problem Statement**
What problem does this solve?

**Proposed Solution**
How would you like it to work?

**Alternatives Considered**
Other solutions you've considered.

**Additional Context**
Any other context or mockups.
```

### Security Issues

**DO NOT** create public issues for security vulnerabilities. Instead:

1. Email security@restaurant-ai.com
2. Include detailed description
3. Provide reproduction steps
4. We'll respond within 24 hours

## Community Guidelines

### Communication

- **Be Respectful**: Treat everyone with respect and kindness
- **Be Constructive**: Provide helpful feedback and suggestions
- **Be Patient**: Remember that everyone is learning
- **Be Inclusive**: Welcome newcomers and different perspectives

### Getting Help

- **Documentation**: Check docs first
- **Discussions**: Use GitHub Discussions for questions
- **Discord**: Join our Discord for real-time chat
- **Stack Overflow**: Tag questions with `restaurant-ai-platform`

### Mentorship

New to open source? We provide mentorship:

- **Good First Issues**: Issues tagged for beginners
- **Pair Programming**: Schedule sessions with maintainers
- **Code Review**: Detailed feedback on contributions
- **Office Hours**: Weekly sessions for questions

## Recognition

### Contributors

All contributors are recognized in:

- **README**: Contributors section
- **Release Notes**: Attribution for features/fixes
- **Hall of Fame**: Top contributors page
- **Swag**: Stickers and shirts for regular contributors

### Levels of Recognition

- **First Contribution**: Welcome package
- **5 Contributions**: Contributor badge
- **10 Contributions**: Core contributor status
- **25 Contributions**: Maintainer consideration

### Annual Awards

- **Most Helpful**: Best community support
- **Most Innovative**: Creative solutions
- **Most Dedicated**: Consistent contributions
- **Rising Star**: Outstanding new contributor

---

Thank you for contributing to the Restaurant AI Platform! Your contributions help make the restaurant industry more accessible and engaging for everyone. 🍽️🤖

For questions, reach out to us at [contribute@restaurant-ai.com](mailto:contribute@restaurant-ai.com).