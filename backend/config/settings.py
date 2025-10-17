from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings and environment variables"""
    
    # Supabase Configuration (required - set in .env file)
    SUPABASE_URL: str
    SUPABASE_KEY: str
    SUPABASE_JWT_SECRET: str
    STORAGE_BUCKET_NAME: str = "food-images"
    
    # ML Service Configuration (optional)
    ML_SERVICE_URL: Optional[str] = None
    
    # Application Configuration
    ENVIRONMENT: str = "development"
    APP_NAME: str = "Food App API"
    APP_VERSION: str = "1.0.0"
    
    # CORS Settings
    CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:3001"]
    
    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        case_sensitive = True


# Global settings instance
settings = Settings()

