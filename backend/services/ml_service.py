from typing import Dict, Optional
import httpx
from backend.config.settings import settings


class MLService:
    """Service for integrating with ML food recognition model"""
    
    def __init__(self):
        self.ml_service_url = settings.ML_SERVICE_URL
        self.timeout = 30.0  # 30 second timeout for ML inference
    
    async def analyze_food_image(self, image_base64: str) -> Dict:
        """
        Call ML service to analyze food image
        
        Args:
            image_base64: Base64 encoded food image
            
        Returns:
            Dict with food_name, category, healthiness_score, calories
        """
        # If ML service URL is not configured, return mock data
        if not self.ml_service_url:
            return self._get_mock_response()
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.ml_service_url}/analyze",
                    json={"image": image_base64}
                )
                response.raise_for_status()
                return response.json()
        except httpx.TimeoutException:
            print("ML service timeout, returning mock response")
            return self._get_mock_response()
        except httpx.HTTPError as e:
            print(f"ML service error: {e}, returning mock response")
            return self._get_mock_response()
        except Exception as e:
            print(f"Unexpected error calling ML service: {e}")
            return self._get_mock_response()
    
    def _get_mock_response(self) -> Dict:
        """
        Return mock ML response for development/testing
        
        Returns:
            Mock food analysis data
        """
        return {
            "food_name": "Apple",
            "category": "fruit",
            "healthiness_score": 85,
            "calories": 95,
            "confidence": 0.92
        }


# Global service instance
ml_service = MLService()

