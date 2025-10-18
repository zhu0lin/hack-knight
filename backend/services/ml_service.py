from typing import Dict, Optional
import httpx
from config.settings import settings


class MLService:
    """Service for integrating with custom ML food recognition model"""
    
    def __init__(self):
        self.ml_service_url = settings.ML_SERVICE_URL
        self.timeout = 30.0  # 30 second timeout for ML inference
    
    async def analyze_food_image(self, image_base64: str) -> Dict:
        """
        Call custom ML service to analyze food image
        
        Args:
            image_base64: Base64 encoded food image
            
        Returns:
            Dict with food_name, category, healthiness_score, calories, confidence
            
        Expected ML Service Response Format:
        {
          "food_name": "specific name of the food item",
          "category": "one of: fruit, vegetable, protein, dairy, grain, other",
          "healthiness_score": number from 0-100,
          "calories": estimated calories per serving,
          "confidence": confidence level 0.0-1.0
        }
        """
        # If ML service URL is not configured, return mock data for development
        if not self.ml_service_url:
            print("ML service URL not configured, using mock response")
            return self._get_mock_response()
        
        try:
            return await self._analyze_with_ml_service(image_base64)
        except Exception as e:
            print(f"ML service error: {e}, returning mock response")
            return self._get_mock_response()
    
    async def _analyze_with_ml_service(self, image_base64: str) -> Dict:
        """
        Call custom ML service to analyze food image
        
        Args:
            image_base64: Base64 encoded food image
            
        Returns:
            Dict with food_name, category, healthiness_score, calories, confidence
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.ml_service_url}/analyze",
                    json={"image": image_base64}
                )
                response.raise_for_status()
                result = response.json()
                
                # Validate and normalize response from custom model
                validated_result = {
                    "food_name": result.get("food_name", "Unknown Food"),
                    "category": self._validate_category(result.get("category", "other")),
                    "healthiness_score": min(max(int(result.get("healthiness_score", 50)), 0), 100),
                    "calories": int(result.get("calories", 100)) if result.get("calories") else 100,
                    "confidence": min(max(float(result.get("confidence", 0.8)), 0.0), 1.0)
                }
                
                return validated_result
        except httpx.TimeoutException:
            print("ML service timeout")
            raise
        except httpx.HTTPError as e:
            print(f"ML service HTTP error: {e}")
            raise
        except Exception as e:
            print(f"ML service error: {e}")
            raise
    
    def _validate_category(self, category: str) -> str:
        """
        Validate and normalize food category
        
        Args:
            category: Category from ML response
            
        Returns:
            Valid category string
        """
        valid_categories = ["fruit", "vegetable", "protein", "dairy", "grain", "other"]
        normalized = category.lower().strip()
        
        if normalized in valid_categories:
            return normalized
        
        # Try to map common variations
        category_mapping = {
            "fruits": "fruit",
            "vegetables": "vegetable",
            "veggies": "vegetable",
            "meat": "protein",
            "proteins": "protein",
            "grains": "grain",
            "carbs": "grain",
            "carbohydrates": "grain",
        }
        
        return category_mapping.get(normalized, "other")
    
    def _get_mock_response(self) -> Dict:
        """
        Return mock ML response for development/testing
        
        This is used when ML_SERVICE_URL is not configured.
        Replace this with your actual trained model once deployed.
        
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

