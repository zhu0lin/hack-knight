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
- 🤖 **Custom ML Food Recognition** - Automatic food detection, categorization, and health scoring using your trained model
- 📊 **Nutrition Tracking** - Track daily intake across all food groups
- 🎯 **Weight Goal Personalization** - Personalized recommendations for weight loss, gain, maintenance, or diabetes management
- 🔥 **Streak Tracking** - Monitor consecutive days of balanced nutrition
- 📈 **Analytics Dashboard** - View daily and weekly summaries
- 💬 **AI Nutrition Chatbot** - Goal-aware chatbot (optional: uses Gemini API if configured)
- 🎨 **Personalized Recommendations** - Calorie targets and meal suggestions based on your goals

### Future Features (Planned)
- 👥 **Social Features** - Friend groups and accountability
- 📱 **Mobile App** - React Native mobile version

## 🏗️ Tech Stack

### Frontend
- **Next.js 14** - React framework with App Router
- **TypeScript** - Type-safe development
- **React 18** - Modern UI components

### Backend
- **FastAPI** - High-performance Python API
- **Supabase** - PostgreSQL database, authentication, and storage
- **Python 3.11** - Modern Python with async support
- **Custom ML Model** - Your trained food recognition model (deployed separately)

### Infrastructure
- **Docker** - Containerization for both services
- **Docker Compose** - Multi-container orchestration
- **Supabase Storage** - Image storage
- **ML Service** - Your custom trained food recognition model (to be deployed)

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
| [CLOUDFLARE_DEPLOYMENT_GUIDE.md](docs/CLOUDFLARE_DEPLOYMENT_GUIDE.md) | **⭐ NEW:** Complete deployment guide (Cloudflare + Railway) |
| [CUSTOM_ML_MODEL_GUIDE.md](docs/CUSTOM_ML_MODEL_GUIDE.md) | **NEW:** How to integrate your trained ML model |
| [WEIGHT_GOALS_AND_VISION_API.md](docs/WEIGHT_GOALS_AND_VISION_API.md) | Weight goals personalization features |
| [API_QUICK_REFERENCE.md](docs/API_QUICK_REFERENCE.md) | Quick reference for API endpoints |
| [ML_MODEL_CHANGES_SUMMARY.md](docs/ML_MODEL_CHANGES_SUMMARY.md) | ML model integration changes |
| [CHATBOT_UPDATE.md](docs/CHATBOT_UPDATE.md) | Chatbot features and examples |

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
- `GET /api/goals/recommendations` - Personalized nutrition recommendations by goal
- `POST /api/goals/calculate-calories` - Calculate personalized calorie target

### Chatbot
- `POST /api/chatbot/chat` - Chat with AI nutrition assistant
- `GET /api/chatbot/missing-groups` - Quick: What food groups am I missing?
- `GET /api/chatbot/meal-suggestions` - Quick: What should I eat next?
- `GET /api/chatbot/nutrition-tips` - Quick: Give me nutrition tips

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
# Supabase Configuration (required)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_JWT_SECRET=your-jwt-secret
STORAGE_BUCKET_NAME=food-images

# Custom ML Model (set when you deploy your trained model)
ML_SERVICE_URL=http://your-ml-service-url/api  # URL to your custom food recognition model

# Optional: Gemini API for chatbot (leave empty to disable chatbot)
GEMINI_API_KEY=  # Optional - only needed if using AI chatbot
GEMINI_MODEL=gemini-pro

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
| **ML Service Integration** | ✅ **Complete** | **100%** |
| **Weight Goal Personalization** | ✅ **Complete** | **100%** |
| **AI Nutrition Chatbot** | ✅ **Complete** | **100%** |
| Food Upload Endpoint | ✅ Complete | 100% |
| Custom ML Model Deployment | 📋 Planned | 0% |
| Analytics Endpoints | ✅ Complete | 100% |
| Auth Implementation | 🔨 In Progress | 50% |
| Frontend-Backend Integration | 🔨 In Progress | 30% |
| Social Features | 📋 Planned | 0% |

**Overall Progress: ~80%**

See [IMPLEMENTATION_SUMMARY.md](docs/IMPLEMENTATION_SUMMARY.md) for details.

## 🚀 Deployment

### Quick Deploy (Recommended)

**Frontend**: Cloudflare Pages (Free)  
**Backend**: Railway (Free tier available)  
**Database**: Supabase (Free tier sufficient)

#### Option 1: Automated Scripts

```bash
# Deploy everything
./deploy-all.sh

# Or deploy individually
./deploy-railway.sh      # Backend
./deploy-cloudflare.sh   # Frontend
```

#### Option 2: Manual via GitHub

1. **Push to GitHub**
   ```bash
   git push origin main
   ```

2. **Deploy Backend to Railway**
   - Go to [railway.app](https://railway.app)
   - Connect GitHub repo
   - Select `backend` folder
   - Add environment variables
   - Deploy

3. **Deploy Frontend to Cloudflare Pages**
   - Go to [Cloudflare Dashboard](https://dash.cloudflare.com)
   - Pages → Create project
   - Connect GitHub repo
   - Root directory: `frontend`
   - Build command: `npm run build`
   - Set env: `NEXT_PUBLIC_API_URL=<railway-url>`
   - Deploy

📖 **Full Guide**: [docs/CLOUDFLARE_DEPLOYMENT_GUIDE.md](docs/CLOUDFLARE_DEPLOYMENT_GUIDE.md)

---

## 🎯 Next Steps

### Immediate (This Week)
1. ✅ Set up Supabase database with SQL scripts
2. ✅ Implement food upload endpoint
3. ✅ Implement weight goal personalization
4. ✅ Integrate AI chatbot with goal awareness
5. 🔨 Deploy to production
6. 🔨 Build frontend food upload UI
7. 🔨 Connect frontend to backend APIs

### Short Term (Next 2 Weeks)
8. Deploy ML model
9. Build goal setting UI
10. Build nutrition dashboard UI
11. Add chatbot UI component
12. User testing and feedback

### Long Term
13. Social features (friend groups)
14. Mobile app (React Native)
15. Advanced meal planning
16. Portion size detection
17. Recipe analysis

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
