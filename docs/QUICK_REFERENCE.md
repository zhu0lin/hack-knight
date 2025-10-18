# Food App - Quick Reference

## 🚀 Start Commands

```bash
# Start everything (recommended)
docker-compose -f docker-compose.dev.yml up -d --build

# View logs
docker-compose -f docker-compose.dev.yml logs -f

# Stop everything
docker-compose -f docker-compose.dev.yml down
```

## 🔗 URLs

- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

## 📂 Key Files

### Backend Structure
```
backend/
├── main.py                     # FastAPI app entry
├── config/settings.py          # Environment config
├── routes/                     # API endpoints
│   ├── auth.py                # Authentication
│   ├── users.py               # User profile
│   ├── food.py                # Food logging
│   ├── goals.py               # Goal management
│   └── analytics.py           # Analytics & streaks
├── services/                   # Business logic
│   ├── supabase_client.py     # Database connection
│   ├── auth_service.py        # Auth logic
│   ├── food_service.py        # Food logging
│   ├── ml_service.py          # ML integration
│   ├── storage_service.py     # Image upload
│   └── nutrition_service.py   # Nutrition calculations
├── schemas/                    # Request/Response models
└── utils/                      # Utilities
    ├── dependencies.py         # Auth middleware
    └── exceptions.py           # Error handling
```

## 🔑 Environment Variables

### Backend (.env)
```env
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=xxx
SUPABASE_JWT_SECRET=xxx
STORAGE_BUCKET_NAME=food-images
ML_SERVICE_URL=
ENVIRONMENT=development
```

## 📋 API Endpoints Summary

### Auth
- `POST /api/auth/signup`
- `POST /api/auth/login`
- `GET /api/auth/me`

### Users
- `GET /api/users/profile`
- `PUT /api/users/profile`
- `POST /api/users/onboarding`

### Food
- `POST /api/food/upload` - Upload image
- `GET /api/food/logs` - Get logs
- `GET /api/food/logs/{id}` - Get one
- `PUT /api/food/logs/{id}` - Update
- `DELETE /api/food/logs/{id}` - Delete

### Goals
- `POST /api/goals` - Create/update
- `GET /api/goals` - Get active
- `GET /api/goals/recommendations`

### Analytics
- `GET /api/analytics/today`
- `GET /api/analytics/week`
- `GET /api/analytics/missing`
- `GET /api/analytics/streak`

## 🗄️ Database Tables

1. **users** - User profiles
2. **user_goals** - Health goals
3. **food_logs** - Food entries
4. **daily_nutrition_summary** - Daily aggregates
5. **user_streaks** - Streak tracking

SQL scripts in: `docs/SETUP_GUIDE.md`

## 🛠️ Common Tasks

### Add New Endpoint
1. Add route in `routes/{module}.py`
2. Add business logic in `services/{module}_service.py`
3. Add schemas in `schemas/{module}_schemas.py`
4. Use `Depends(get_current_user_id)` for auth

### Run Tests
```bash
docker-compose -f docker-compose.dev.yml exec backend pytest
```

### Access Database
Use Supabase dashboard or SQL editor

### Check Logs
```bash
docker-compose -f docker-compose.dev.yml logs backend
docker-compose -f docker-compose.dev.yml logs frontend
```

### Restart Service
```bash
docker-compose -f docker-compose.dev.yml restart backend
docker-compose -f docker-compose.dev.yml restart frontend
```

### Rebuild After Changes
```bash
docker-compose -f docker-compose.dev.yml up -d --build
```

## 🐛 Debugging

### Backend Not Starting
1. Check `.env` file exists with correct values
2. View logs: `docker-compose -f docker-compose.dev.yml logs backend`
3. Check port 8000 is available

### Frontend Not Connecting to Backend
1. Verify `NEXT_PUBLIC_API_URL=http://localhost:8000`
2. Check CORS settings in `backend/main.py`
3. Verify backend is running at port 8000

### Supabase Connection Error
1. Verify credentials in `.env`
2. Check Supabase project is active
3. Ensure tables are created (run SQL scripts)

### Import Errors
1. Ensure you're in backend directory
2. Check all `__init__.py` files exist
3. Verify dependencies installed: `pip install -r requirements.txt`

## 📚 Documentation

- **PROJECT_CONTEXT.md** - Full project overview
- **BACKEND_ARCHITECTURE.md** - Architecture details
- **SETUP_GUIDE.md** - Setup instructions
- **IMPLEMENTATION_SUMMARY.md** - What's done/todo

## 🎯 Next Implementation Steps

1. Implement auth routes (use `auth_service`)
2. Implement food upload (use `storage_service` + `ml_service`)
3. Implement analytics routes (use `nutrition_service`)
4. Connect frontend to backend
5. Add error handling
6. Write tests

## 💡 Code Snippets

### Protected Route
```python
from fastapi import Depends
from backend.utils.dependencies import get_current_user_id

@router.get("/profile")
async def get_profile(user_id: str = Depends(get_current_user_id)):
    # user_id is automatically extracted from JWT
    return {"user_id": user_id}
```

### Use Service
```python
from backend.services.food_service import food_service

@router.get("/logs")
async def get_logs(user_id: str = Depends(get_current_user_id)):
    logs = await food_service.get_food_logs(user_id)
    return {"logs": logs}
```

### Use Schema
```python
from backend.schemas.food_schemas import FoodUploadRequest

@router.post("/upload")
async def upload(
    request: FoodUploadRequest,
    user_id: str = Depends(get_current_user_id)
):
    # request is validated by Pydantic
    image = request.image_base64
    # ... your logic
```

---

**Keep this file handy for quick reference during development!**

