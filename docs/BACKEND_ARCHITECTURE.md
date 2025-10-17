# Food App Backend Architecture Plan

## Overview

Design a scalable FastAPI backend with organized routes, business logic, and integrations for Supabase (database, auth, storage) and a custom ML food recognition service.

## 1. Project Structure

Create organized backend structure:

```
backend/
├── main.py                      # FastAPI app entry point
├── requirements.txt             # Dependencies
├── config/
│   └── settings.py             # Environment variables, Supabase config
├── models/
│   ├── __init__.py
│   ├── user.py                 # User data models
│   ├── food_log.py             # Food entry models
│   ├── goal.py                 # User goals models
│   └── streak.py               # Streak tracking models
├── routes/
│   ├── __init__.py
│   ├── auth.py                 # Authentication endpoints
│   ├── users.py                # User profile endpoints
│   ├── food.py                 # Food logging endpoints
│   ├── goals.py                # Goal management endpoints
│   ├── analytics.py            # Daily summary, nutrition tracking
│   └── social.py               # Friends, streaks (future)
├── services/
│   ├── __init__.py
│   ├── supabase_client.py      # Supabase connection
│   ├── auth_service.py         # Auth business logic
│   ├── food_service.py         # Food logging business logic
│   ├── ml_service.py           # ML model integration
│   ├── nutrition_service.py    # Nutrition calculations
│   └── storage_service.py      # Image upload/retrieval
├── schemas/
│   ├── __init__.py
│   ├── user_schemas.py         # Pydantic request/response models
│   ├── food_schemas.py         # Food entry schemas
│   └── goal_schemas.py         # Goal schemas
└── utils/
    ├── __init__.py
    ├── dependencies.py         # FastAPI dependencies (auth middleware)
    └── exceptions.py           # Custom exceptions
```

## 2. Database Schema (Supabase PostgreSQL)

### Tables to create in Supabase:

**users** (extends Supabase auth.users)
```sql
- id (uuid, FK to auth.users)
- created_at (timestamp)
- full_name (text)
- avatar_url (text)
- current_weight (decimal, nullable)
- target_weight (decimal, nullable)
- height (decimal, nullable)
- age (integer, nullable)
```

**user_goals**
```sql
- id (uuid, PK)
- user_id (uuid, FK to users)
- goal_type (enum: 'maintain', 'lose_weight', 'gain_weight', 'diabetes_management')
- target_calories (integer, nullable)
- created_at (timestamp)
- is_active (boolean)
```

**food_logs**
```sql
- id (uuid, PK)
- user_id (uuid, FK to users)
- image_url (text)
- detected_food_name (text)
- food_category (enum: 'fruit', 'vegetable', 'protein', 'dairy', 'grain', 'other')
- healthiness_score (integer, 0-100)
- calories (integer, nullable)
- meal_type (enum: 'breakfast', 'lunch', 'dinner', 'snack')
- logged_at (timestamp)
- created_at (timestamp)
```

**daily_nutrition_summary**
```sql
- id (uuid, PK)
- user_id (uuid, FK to users)
- date (date, unique with user_id)
- fruits_count (integer)
- vegetables_count (integer)
- protein_count (integer)
- dairy_count (integer)
- grains_count (integer)
- total_calories (integer)
- completion_percentage (integer)
- created_at (timestamp)
```

**user_streaks**
```sql
- id (uuid, PK)
- user_id (uuid, FK to users, unique)
- current_streak (integer)
- longest_streak (integer)
- last_logged_date (date)
- updated_at (timestamp)
```

## 3. API Routes & Endpoints

### Authentication Routes (`routes/auth.py`)

```
POST   /api/auth/signup          - Create account with Supabase OAuth
POST   /api/auth/login           - Login with OAuth provider
POST   /api/auth/logout          - Logout user
GET    /api/auth/me              - Get current user info
```

### User Routes (`routes/users.py`)

```
GET    /api/users/profile        - Get user profile
PUT    /api/users/profile        - Update profile (weight, height, etc)
POST   /api/users/onboarding     - Complete initial setup (goals, preferences)
```

### Goal Routes (`routes/goals.py`)

```
POST   /api/goals                - Create/update user goal
GET    /api/goals                - Get user's active goal
GET    /api/goals/recommendations - Get personalized nutrition recommendations
```

### Food Routes (`routes/food.py`)

```
POST   /api/food/upload          - Upload food image, analyze with ML
GET    /api/food/logs            - Get user's food logs (with filters)
GET    /api/food/logs/{id}       - Get specific food log
DELETE /api/food/logs/{id}       - Delete food log
PUT    /api/food/logs/{id}       - Edit food log details
```

### Analytics Routes (`routes/analytics.py`)

```
GET    /api/analytics/today      - Today's nutrition summary
GET    /api/analytics/week       - Weekly nutrition summary
GET    /api/analytics/missing    - What food groups are missing today
GET    /api/analytics/streak     - Get user's current streak
```

### Social Routes (`routes/social.py`) - Future feature

```
GET    /api/social/friends       - Get friends list
POST   /api/social/friends       - Add friend
GET    /api/social/leaderboard   - Friends streak leaderboard
```

## 4. Business Logic (Services)

### `services/auth_service.py`
- Verify Supabase JWT tokens
- Get user from token
- Handle OAuth flow
- Create user profile on first signup

### `services/food_service.py`
- Handle food log creation
- Update daily nutrition summary
- Query food logs with filters
- Update user streak on food log

### `services/ml_service.py`
- Call ML model endpoint (POST to separate microservice)
- Request format: `{"image": base64_string}`
- Response format: `{"food_name": str, "category": str, "healthiness_score": int, "calories": int}`
- Handle ML service errors/timeouts

### `services/storage_service.py`
- Upload images to Supabase Storage bucket
- Generate signed URLs for image access
- Delete images from storage

### `services/nutrition_service.py`
- Calculate daily nutrition completion
- Determine missing food groups
- Generate personalized recommendations based on goals
- Update streak logic (consecutive days of complete nutrition)

## 5. Pydantic Schemas

### `schemas/user_schemas.py`
```python
UserProfileResponse, UserProfileUpdate, OnboardingRequest
```

### `schemas/food_schemas.py`
```python
FoodUploadResponse, FoodLogResponse, FoodLogCreate, FoodLogUpdate
```

### `schemas/goal_schemas.py`
```python
GoalCreate, GoalResponse, NutritionRecommendation
```

## 6. Key Integrations

### Supabase Integration (`services/supabase_client.py`)
- Initialize Supabase client with API key and URL
- Use `supabase-py` library
- Handle database queries
- Handle storage operations
- Verify auth tokens

### ML Model Integration (`services/ml_service.py`)
- HTTP client to call ML service endpoint
- Configurable ML service URL via environment variable
- Retry logic for failed requests
- Fallback responses for development

### Authentication Middleware (`utils/dependencies.py`)
- FastAPI dependency to verify Supabase JWT
- Extract user_id from token
- Protect routes requiring authentication

## 7. Configuration (`config/settings.py`)

Environment variables to add:
```python
SUPABASE_URL
SUPABASE_KEY
SUPABASE_JWT_SECRET
ML_SERVICE_URL
STORAGE_BUCKET_NAME="food-images"
ENVIRONMENT
```

## 8. Dependencies to Add

Update `requirements.txt`:
```
fastapi==0.109.0
uvicorn[standard]==0.27.0
pydantic==2.5.3
python-dotenv==1.0.0
supabase==2.3.0          # New
httpx==0.26.0            # New (for ML service calls)
python-jose[cryptography]==3.3.0  # New (JWT handling)
python-multipart==0.0.6  # New (file uploads)
Pillow==10.2.0           # New (image processing)
```

## 9. Implementation Order

1. Set up project structure (folders, __init__.py files)
2. Create configuration and Supabase client
3. Create Pydantic schemas for all models
4. Implement authentication service and routes
5. Implement user profile routes
6. Implement goal management
7. Implement storage service (image upload)
8. Implement ML service integration (with mock responses)
9. Implement food logging routes and business logic
10. Implement nutrition analytics and streak calculation
11. Update main.py to register all routes
12. Document all endpoints in PROJECT_CONTEXT.md

## Key Design Decisions

- **Separation of Concerns**: Routes handle HTTP, services handle business logic, schemas validate data
- **Supabase RLS**: Use Row Level Security in Supabase for database-level access control
- **Async/Await**: Use async functions for I/O operations (database, ML service calls)
- **JWT Middleware**: FastAPI dependency injection for authentication
- **ML Service Independence**: Backend doesn't depend on ML implementation details
- **Image Storage**: Store images in Supabase Storage, only store URLs in database
- **Daily Summaries**: Pre-calculated table for fast analytics queries
- **Streak Logic**: Updated on each successful food log with complete nutrition day

