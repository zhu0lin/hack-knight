from typing import Optional
import base64
from datetime import datetime
import uuid
from services.supabase_client import get_supabase
from config.settings import settings


class StorageService:
    """Service for handling image uploads to Supabase Storage"""
    
    def __init__(self):
        self.supabase = None
        self.bucket_name = settings.STORAGE_BUCKET_NAME
    
    def _get_supabase(self):
        """Lazy load Supabase client"""
        if self.supabase is None:
            self.supabase = get_supabase()
        return self.supabase
    
    async def upload_food_image(self, user_id: str, image_data: bytes, file_extension: str = "jpg") -> str:
        """
        Upload food image to Supabase Storage
        
        Args:
            user_id: User's UUID
            image_data: Image file bytes
            file_extension: File extension (jpg, png, etc)
            
        Returns:
            Public URL of uploaded image
        """
        try:
            # Generate unique filename
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            unique_id = str(uuid.uuid4())[:8]
            filename = f"{user_id}/{timestamp}_{unique_id}.{file_extension}"
            
            # Upload to Supabase Storage
            supabase = self._get_supabase()
            response = supabase.storage.from_(self.bucket_name).upload(
                path=filename,
                file=image_data,
                file_options={"content-type": f"image/{file_extension}"}
            )
            
            # Get public URL
            public_url = supabase.storage.from_(self.bucket_name).get_public_url(filename)
            
            return public_url
        except Exception as e:
            print(f"Error uploading image: {e}")
            raise
    
    async def delete_food_image(self, image_url: str) -> bool:
        """
        Delete food image from Supabase Storage
        
        Args:
            image_url: Full URL of the image to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Extract filename from URL
            # URL format: https://.../storage/v1/object/public/bucket-name/path/to/file.jpg
            filename = image_url.split(f"{self.bucket_name}/")[-1]
            
            self._get_supabase().storage.from_(self.bucket_name).remove([filename])
            return True
        except Exception as e:
            print(f"Error deleting image: {e}")
            return False
    
    async def get_signed_url(self, image_path: str, expires_in: int = 3600) -> Optional[str]:
        """
        Generate signed URL for private image access
        
        Args:
            image_path: Path to image in storage bucket
            expires_in: URL expiration time in seconds (default 1 hour)
            
        Returns:
            Signed URL or None if error
        """
        try:
            response = self._get_supabase().storage.from_(self.bucket_name).create_signed_url(
                path=image_path,
                expires_in=expires_in
            )
            return response.get("signedURL")
        except Exception as e:
            print(f"Error generating signed URL: {e}")
            return None


# Global service instance
storage_service = StorageService()

