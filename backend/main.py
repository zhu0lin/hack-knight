from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from config.settings import settings

# Import all route modules
from routes import auth, users, food, goals, analytics, social, chatbot, dev

app = FastAPI(
    title=settings.APP_NAME,
    description="Backend API for Food App - Track your nutrition and reach your health goals",
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all route modules
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(food.router)
app.include_router(goals.router)
app.include_router(analytics.router)
app.include_router(social.router)
app.include_router(chatbot.router)
app.include_router(dev.router)  # Development/testing endpoints

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Food App API! 🍎",
        "description": "Track your nutrition, achieve your health goals",
        "timestamp": datetime.now().isoformat(),
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "environment": settings.ENVIRONMENT,
        "version": settings.APP_VERSION
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

