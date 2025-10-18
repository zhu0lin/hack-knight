# 🍎 Food App - Nutrition Tracking Platform

A full-stack application for tracking nutrition, achieving health goals, and maintaining healthy eating habits.

## 📋 Problem Statement

For busy adults, finding time to cook healthy meals is challenging. This leads to unhealthy takeout habits. According to the 2020 National Health Interview Survey (NHIS), only 24% of adults in the United States consume a balanced diet daily. This app helps users track their nutrition and achieve their health goals.

## 🎯 Target Audience

- Busy adults seeking better nutrition
- People with weight management goals (gain/loss)
- Individuals managing diabetes
- Anyone wanting to maintain a balanced diet

## ✨ Core Features

### Current MVP Features
- 📸 **Food Image Upload** - Take or upload photos of meals
- 🤖 **ML Food Recognition** - Automatic food categorization and health scoring
- 📊 **Nutrition Tracking** - Track daily intake across food groups
- 🎯 **Goal Setting** - Personalize for weight loss, gain, or maintenance
- 🔥 **Streak Tracking** - Monitor consecutive days of balanced nutrition
- 📈 **Analytics Dashboard** - View daily and weekly summaries

### Future Features (Planned)
- 💬 **AI Chatbot** - Quick answers to nutrition questions
- 👥 **Social Features** - Friend groups and accountability
- 🎨 **Personalized Recommendations** - Based on goals and preferences

## 🏗️ Tech Stack

### Frontend
- **Next.js 14** - React framework with App Router
- **TypeScript** - Type-safe development
- **React 18** - Modern UI components

### Backend
- **FastAPI** - High-performance Python API
- **Supabase** - PostgreSQL database, authentication, and storage
- **Python 3.11** - Modern Python with async support

### Infrastructure
- **Docker** - Containerization for both services
- **Docker Compose** - Multi-container orchestration
- **Supabase Storage** - Image storage
- **Custom ML Service** - Food recognition model (to be deployed)

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Supabase account (free tier works)
- Node.js 20+ (if running locally without Docker)
- Python 3.11+ (if running locally without Docker)

### 1. Clone and Setup

```bash
cd hack-knight

# Copy environment file
cp backend/.env.example backend/.env
# Edit backend/.env with your Supabase credentials
```

### 2. Start with Docker

```bash
# Start both frontend and backend with hot-reloading
docker-compose -f docker-compose.dev.yml up -d --build

# View logs
docker-compose -f docker-compose.dev.yml logs -f
```

### 3. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Alternative API Docs**: http://localhost:8000/redoc

## 📖 Documentation

Comprehensive documentation is available in the `docs/` folder:

| Document | Description |
|----------|-------------|
| [PROJECT_CONTEXT.md](docs/PROJECT_CONTEXT.md) | Overall project architecture and workflow |
| [BACKEND_ARCHITECTURE.md](docs/BACKEND_ARCHITECTURE.md) | Complete backend design and architecture |
| [SETUP_GUIDE.md](docs/SETUP_GUIDE.md) | Step-by-step setup with SQL scripts |
| [IMPLEMENTATION_SUMMARY.md](docs/IMPLEMENTATION_SUMMARY.md) | What's built and what's next |

## 🗄️ Database Schema

The app uses 5 main tables in Supabase:

1. **users** - User profiles with health metrics
2. **user_goals** - Health goals (weight loss/gain, diabetes management)
3. **food_logs** - Individual food entries with ML analysis
4. **daily_nutrition_summary** - Aggregated daily nutrition data
5. **user_streaks** - Streak tracking for user engagement

See [SETUP_GUIDE.md](docs/SETUP_GUIDE.md) for complete SQL schemas.

## 🔌 API Endpoints

### Authentication
- `POST /api/auth/signup` - Create account
- `POST /api/auth/login` - Login with OAuth
- `GET /api/auth/me` - Get current user

### Food Tracking
- `POST /api/food/upload` - Upload and analyze food image
- `GET /api/food/logs` - Get user's food history
- `PUT /api/food/logs/{id}` - Update food entry
- `DELETE /api/food/logs/{id}` - Delete food entry

### Analytics
- `GET /api/analytics/today` - Today's nutrition summary
- `GET /api/analytics/week` - Weekly overview
- `GET /api/analytics/missing` - Missing food groups
- `GET /api/analytics/streak` - Current streak

### Goals
- `POST /api/goals` - Set health goal
- `GET /api/goals` - Get active goal
- `GET /api/goals/recommendations` - Personalized recommendations

Full API documentation at http://localhost:8000/docs

## 📁 Project Structure

```
hack-knight/
├── frontend/                 # Next.js application
│   ├── app/                 # App router pages
│   ├── Dockerfile           # Production container
│   └── Dockerfile.dev       # Development container
│
├── backend/                 # FastAPI application
│   ├── config/             # Configuration management
│   ├── models/             # Data models
│   ├── routes/             # API endpoints
│   ├── services/           # Business logic
│   ├── schemas/            # Pydantic validation
│   ├── utils/              # Utilities & middleware
│   ├── main.py             # FastAPI entry point
│   ├── Dockerfile          # Production container
│   └── Dockerfile.dev      # Development container
│
├── docs/                    # Project documentation
│   ├── PROJECT_CONTEXT.md
│   ├── BACKEND_ARCHITECTURE.md
│   ├── SETUP_GUIDE.md
│   └── IMPLEMENTATION_SUMMARY.md
│
├── docker-compose.yml       # Production orchestration
├── docker-compose.dev.yml   # Development orchestration
└── README.md               # This file
```

## 🛠️ Development

### Run Frontend Only

```bash
cd frontend
npm install
npm run dev
```

### Run Backend Only

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### Run Both with Docker

```bash
# Development mode (recommended)
docker-compose -f docker-compose.dev.yml up -d --build

# Production mode
docker-compose up --build
```

## 🧪 Testing the API

### Using Swagger UI (Recommended)
1. Navigate to http://localhost:8000/docs
2. Try the `/health` endpoint
3. For protected endpoints, click "Authorize" and enter your JWT token

### Using cURL
```bash
# Health check
curl http://localhost:8000/health

# Get today's summary (requires auth token)
curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://localhost:8000/api/analytics/today
```

## 🔐 Environment Variables

### Backend (.env)
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_JWT_SECRET=your-jwt-secret
STORAGE_BUCKET_NAME=food-images
ML_SERVICE_URL=  # Optional, uses mock data if not set
ENVIRONMENT=development
```

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 📊 Implementation Status

| Component | Status | Progress |
|-----------|--------|----------|
| Frontend Boilerplate | ✅ Complete | 100% |
| Backend Structure | ✅ Complete | 100% |
| Database Models | ✅ Complete | 100% |
| API Routes (Skeleton) | ✅ Complete | 100% |
| Service Layer | ✅ Complete | 100% |
| Auth Implementation | 🔨 In Progress | 0% |
| Food Upload | 🔨 In Progress | 0% |
| Analytics | 🔨 In Progress | 0% |
| ML Model Integration | 📋 Planned | 0% |
| Social Features | 📋 Planned | 0% |

**Overall Progress: ~60%**

See [IMPLEMENTATION_SUMMARY.md](docs/IMPLEMENTATION_SUMMARY.md) for details.

## 🎯 Next Steps

### Immediate (This Week)
1. ✅ Set up Supabase database with SQL scripts
2. 🔨 Implement authentication flow
3. 🔨 Implement food upload endpoint
4. 🔨 Build frontend food upload UI
5. 🔨 Connect frontend to backend APIs

### Short Term (Next 2 Weeks)
6. Deploy ML food recognition model
7. Implement analytics endpoints
8. Build nutrition dashboard UI
9. Add streak visualization
10. User profile and onboarding flow

### Long Term
11. Chatbot integration
12. Social features
13. Mobile app (React Native)
14. Advanced meal planning

## 🤝 Contributing

This is a hackathon project. Contributions welcome!

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📝 License

MIT License - feel free to use this project as a template for your own apps!

## 👥 Team

Built during Hack Knight 2025

## 🔗 Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [Supabase Documentation](https://supabase.com/docs)
- [Docker Documentation](https://docs.docker.com/)

## 📞 Support

For questions or issues:
1. Check the documentation in `docs/`
2. Review API docs at `/docs` endpoint
3. Check existing issues or create a new one

---

**Built with ❤️ for better health and nutrition**
