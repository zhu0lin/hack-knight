from supabase import create_client, Client
from config.settings import settings
from typing import Optional


class SupabaseClient:
    """Singleton Supabase client with lazy initialization"""
    
    _instance: Optional[Client] = None
    _initialized: bool = False
    
    @classmethod
    def get_client(cls) -> Client:
        """
        Get or create Supabase client instance (lazy initialization)
        
        Returns:
            Supabase client instance
            
        Raises:
            Exception: If Supabase credentials are invalid
        """
        if not cls._initialized:
            try:
                cls._instance = create_client(
                    supabase_url=settings.SUPABASE_URL,
                    supabase_key=settings.SUPABASE_KEY
                )
                cls._initialized = True
                print("✅ Supabase client initialized successfully")
            except Exception as e:
                print(f"⚠️  Warning: Could not initialize Supabase client: {e}")
                print("⚠️  The API will start but database operations will fail.")
                print("⚠️  Please check your SUPABASE_URL and SUPABASE_KEY in .env file")
                # Set a flag so we don't try again
                cls._initialized = True
                cls._instance = None
        
        if cls._instance is None:
            raise Exception(
                "Supabase client not available. Please check your credentials in .env file. "
                "Required: SUPABASE_URL, SUPABASE_KEY"
            )
        
        return cls._instance


# Convenience function to get client
def get_supabase() -> Client:
    """Get Supabase client instance"""
    return SupabaseClient.get_client()

