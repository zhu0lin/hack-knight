# Food App - Setup Guide

## Quick Setup

### 1. Environment Variables

Create a `.env` file in the `backend/` directory with your Supabase credentials:

```env
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key-here
SUPABASE_JWT_SECRET=your-jwt-secret-here
STORAGE_BUCKET_NAME=food-images

# ML Service Configuration (optional)
ML_SERVICE_URL=

# Application Configuration
ENVIRONMENT=development
APP_NAME=Food App API
APP_VERSION=1.0.0
```

### 2. Supabase Setup

#### Create Tables

Run these SQL commands in your Supabase SQL editor:

```sql
-- Users table (extends auth.users)
CREATE TABLE users (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    full_name TEXT,
    avatar_url TEXT,
    current_weight DECIMAL,
    target_weight DECIMAL,
    height DECIMAL,
    age INTEGER
);

-- Enable Row Level Security
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- Users can only see and update their own profile
CREATE POLICY "Users can view own profile" ON users
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON users
    FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "Users can insert own profile" ON users
    FOR INSERT WITH CHECK (auth.uid() = id);

-- User goals table
CREATE TABLE user_goals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    goal_type TEXT NOT NULL CHECK (goal_type IN ('maintain', 'lose_weight', 'gain_weight', 'diabetes_management')),
    target_calories INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);

ALTER TABLE user_goals ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can manage own goals" ON user_goals
    FOR ALL USING (auth.uid() = user_id);

-- Food logs table
CREATE TABLE food_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    image_url TEXT NOT NULL,
    detected_food_name TEXT NOT NULL,
    food_category TEXT NOT NULL CHECK (food_category IN ('fruit', 'vegetable', 'protein', 'dairy', 'grain', 'other')),
    healthiness_score INTEGER NOT NULL CHECK (healthiness_score >= 0 AND healthiness_score <= 100),
    calories INTEGER,
    meal_type TEXT CHECK (meal_type IN ('breakfast', 'lunch', 'dinner', 'snack')),
    logged_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

ALTER TABLE food_logs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can manage own food logs" ON food_logs
    FOR ALL USING (auth.uid() = user_id);

-- Daily nutrition summary table
CREATE TABLE daily_nutrition_summary (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    fruits_count INTEGER DEFAULT 0,
    vegetables_count INTEGER DEFAULT 0,
    protein_count INTEGER DEFAULT 0,
    dairy_count INTEGER DEFAULT 0,
    grains_count INTEGER DEFAULT 0,
    total_calories INTEGER DEFAULT 0,
    completion_percentage INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, date)
);

ALTER TABLE daily_nutrition_summary ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own summaries" ON daily_nutrition_summary
    FOR ALL USING (auth.uid() = user_id);

-- User streaks table
CREATE TABLE user_streaks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    current_streak INTEGER DEFAULT 0,
    longest_streak INTEGER DEFAULT 0,
    last_logged_date DATE,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

ALTER TABLE user_streaks ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can manage own streaks" ON user_streaks
    FOR ALL USING (auth.uid() = user_id);
```

#### Create Storage Bucket

1. Go to Storage in your Supabase dashboard
2. Create a new bucket named `food-images`
3. Make it public (or configure RLS policies as needed)

### 3. Start the Application

#### Using Docker (Recommended)

```bash
# Development mode with hot-reloading
docker-compose -f docker-compose.dev.yml up -d --build

# View logs
docker-compose -f docker-compose.dev.yml logs -f backend
```

#### Local Development

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Verify Setup

Visit these URLs to verify everything is working:

- **API Root**: http://localhost:8000
- **Health Check**: http://localhost:8000/health
- **API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Testing

### Using Swagger UI

1. Navigate to http://localhost:8000/docs
2. All endpoints are documented and testable
3. For protected endpoints, click "Authorize" and enter: `Bearer YOUR_JWT_TOKEN`

### Using cURL

```bash
# Health check
curl http://localhost:8000/health

# Get today's analytics (requires auth)
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     http://localhost:8000/api/analytics/today
```

## Available Endpoints

### Authentication
- `POST /api/auth/signup` - Create account
- `POST /api/auth/login` - Login
- `POST /api/auth/logout` - Logout
- `GET /api/auth/me` - Get current user

### User Profile
- `GET /api/users/profile` - Get profile
- `PUT /api/users/profile` - Update profile
- `POST /api/users/onboarding` - Complete onboarding

### Goals
- `POST /api/goals` - Create/update goal
- `GET /api/goals` - Get active goal
- `GET /api/goals/recommendations` - Get recommendations

### Food Logging
- `POST /api/food/upload` - Upload & analyze food image
- `GET /api/food/logs` - Get food logs
- `GET /api/food/logs/{id}` - Get specific log
- `PUT /api/food/logs/{id}` - Update log
- `DELETE /api/food/logs/{id}` - Delete log

### Analytics
- `GET /api/analytics/today` - Today's summary
- `GET /api/analytics/week` - Weekly summary
- `GET /api/analytics/missing` - Missing food groups
- `GET /api/analytics/streak` - User streak

### Social (Future)
- `GET /api/social/friends` - Get friends
- `POST /api/social/friends` - Add friend
- `GET /api/social/leaderboard` - Streak leaderboard

## Next Steps

1. **Implement Authentication Routes**: Add full Supabase OAuth integration
2. **Implement Food Upload**: Complete image upload and ML integration
3. **Add Analytics Logic**: Implement summary calculations
4. **Frontend Integration**: Connect Next.js frontend to these APIs
5. **Add Tests**: Write unit and integration tests
6. **ML Model**: Deploy or integrate your food recognition model

## Troubleshooting

### Import Errors

If you see import errors, ensure you're running from the project root and have installed all dependencies:

```bash
# From hack-knight directory
cd backend
pip install -r requirements.txt
```

### Supabase Connection Issues

- Verify your `.env` file has correct credentials
- Check that your Supabase project is running
- Ensure RLS policies are properly configured

### Port Already in Use

```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Or use different port
uvicorn main:app --reload --port 8001
```

## Project Structure

```
backend/
├── main.py                    # FastAPI app entry
├── requirements.txt           # Dependencies
├── config/
│   └── settings.py           # Configuration
├── models/                   # Data models
├── routes/                   # API endpoints
├── services/                 # Business logic
├── schemas/                  # Pydantic schemas
└── utils/                    # Utilities
```

For detailed architecture information, see [BACKEND_ARCHITECTURE.md](./BACKEND_ARCHITECTURE.md).

