# Custom ML Model Integration Guide

## Overview

The backend is configured to use **your custom trained food recognition model** instead of third-party APIs. This gives you full control over the model and ensures your data stays private.

---

## Expected ML Model API Contract

Your ML service should expose an endpoint that accepts a POST request with a base64-encoded image and returns food analysis data.

### Endpoint

```
POST /analyze
```

### Request Format

```json
{
  "image": "base64_encoded_image_string"
}
```

### Response Format

Your model should return JSON in this exact format:

```json
{
  "food_name": "Grilled Chicken Breast",
  "category": "protein",
  "healthiness_score": 85,
  "calories": 165,
  "confidence": 0.94
}
```

### Field Specifications

| Field | Type | Range | Description |
|-------|------|-------|-------------|
| `food_name` | string | - | Specific name of the food item (e.g., "Grilled Chicken Breast", "Apple", "Caesar Salad") |
| `category` | string | See below | Food category from predefined list |
| `healthiness_score` | integer | 0-100 | How healthy the food is (100 = very healthy) |
| `calories` | integer | 0-9999 | Estimated calories per serving |
| `confidence` | float | 0.0-1.0 | Model's confidence in the prediction |

### Valid Categories

Your model must return one of these **6 categories**:

- `fruit` - All fruits (apples, bananas, berries, oranges, etc.)
- `vegetable` - All vegetables (broccoli, carrots, salads, lettuce, etc.)
- `protein` - Meat, fish, eggs, tofu, beans, nuts, legumes
- `dairy` - Milk, cheese, yogurt, ice cream, butter
- `grain` - Bread, rice, pasta, cereals, oats, quinoa
- `other` - Processed foods, desserts, drinks, mixed dishes

**Category Variations (automatically normalized):**
- "vegetables" → "vegetable"
- "fruits" → "fruit"
- "meat" → "protein"
- "grains" → "grain"
- "carbs" → "grain"

### Healthiness Score Guidelines

Recommend using these ranges:

- **90-100**: Very healthy (raw fruits, vegetables, lean proteins)
- **70-89**: Healthy (whole grains, dairy, cooked vegetables)
- **50-69**: Moderate (mixed dishes, some processed foods)
- **30-49**: Less healthy (fried foods, high sugar/fat)
- **0-29**: Unhealthy (junk food, highly processed)

---

## Backend Configuration

### 1. Environment Variable

Set your ML service URL in `backend/.env`:

```env
ML_SERVICE_URL=http://your-ml-service-url/api
```

**Examples:**
```env
# Local development
ML_SERVICE_URL=http://localhost:5000/api

# Docker container
ML_SERVICE_URL=http://ml-service:5000/api

# Cloud deployment
ML_SERVICE_URL=https://your-ml-model.herokuapp.com/api
```

### 2. How It Works

When a user uploads a food image:

```
1. Frontend sends image to backend
   POST /api/food/upload

2. Backend converts image to base64

3. Backend calls your ML service
   POST {ML_SERVICE_URL}/analyze
   Body: {"image": "base64..."}

4. Your model analyzes and returns JSON

5. Backend validates/normalizes response

6. Backend creates food log in database

7. Frontend displays results
```

---

## Development Without ML Model

If your model isn't deployed yet, the backend will use **mock data** for testing:

```python
# Mock response when ML_SERVICE_URL is not set
{
  "food_name": "Apple",
  "category": "fruit",
  "healthiness_score": 85,
  "calories": 95,
  "confidence": 0.92
}
```

This allows frontend development to proceed while you're training/deploying the model.

---

## Example ML Service Implementation

### Python Flask Example

```python
from flask import Flask, request, jsonify
import base64
import io
from PIL import Image
import your_model  # Your trained model

app = Flask(__name__)

# Load your trained model
model = your_model.load_model('path/to/model.h5')

@app.route('/analyze', methods=['POST'])
def analyze_food():
    try:
        # Get base64 image from request
        data = request.json
        image_base64 = data.get('image')
        
        # Decode base64 to image
        image_bytes = base64.b64decode(image_base64)
        image = Image.open(io.BytesIO(image_bytes))
        
        # Run your model inference
        prediction = model.predict(image)
        
        # Format response
        response = {
            "food_name": prediction['name'],
            "category": prediction['category'],
            "healthiness_score": prediction['healthiness'],
            "calories": prediction['calories'],
            "confidence": prediction['confidence']
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

### FastAPI Example

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import base64
import io
from PIL import Image
import your_model

app = FastAPI()

# Load your trained model
model = your_model.load_model('path/to/model.h5')

class ImageRequest(BaseModel):
    image: str  # base64 encoded

class FoodResponse(BaseModel):
    food_name: str
    category: str
    healthiness_score: int
    calories: int
    confidence: float

@app.post("/analyze", response_model=FoodResponse)
async def analyze_food(request: ImageRequest):
    try:
        # Decode base64 to image
        image_bytes = base64.b64decode(request.image)
        image = Image.open(io.BytesIO(image_bytes))
        
        # Run your model inference
        prediction = model.predict(image)
        
        return FoodResponse(
            food_name=prediction['name'],
            category=prediction['category'],
            healthiness_score=prediction['healthiness'],
            calories=prediction['calories'],
            confidence=prediction['confidence']
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=5000)
```

---

## Docker Deployment

### docker-compose.yml

Add your ML service to the compose file:

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    environment:
      - ML_SERVICE_URL=http://ml-service:5000/api
    depends_on:
      - ml-service
    ports:
      - "8000:8000"
  
  ml-service:
    build: ./ml-service
    ports:
      - "5000:5000"
    volumes:
      - ./ml-service/models:/app/models
  
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
```

---

## Testing Your ML Service

### 1. Test ML Service Directly

```bash
# Encode test image to base64
IMAGE_BASE64=$(base64 -i test_image.jpg)

# Test your ML service
curl -X POST "http://localhost:5000/analyze" \
  -H "Content-Type: application/json" \
  -d "{\"image\": \"$IMAGE_BASE64\"}"

# Expected response:
{
  "food_name": "Grilled Chicken",
  "category": "protein",
  "healthiness_score": 88,
  "calories": 165,
  "confidence": 0.94
}
```

### 2. Test Through Backend

```bash
# Upload image through backend
curl -X POST "http://localhost:8000/api/food/upload" \
  -F "image=@test_image.jpg" \
  -F "user_id=test-user-id" \
  -F "meal_type=lunch"

# Backend will call your ML service and return results
```

### 3. Test in Swagger UI

1. Go to http://localhost:8000/docs
2. Find `POST /api/food/upload`
3. Click "Try it out"
4. Upload an image
5. See your model's predictions!

---

## Error Handling

### Timeout

- Default timeout: 30 seconds
- If your model takes longer, backend will return mock data
- Optimize your model for faster inference (<5 seconds recommended)

### Service Unavailable

- If ML service is down, backend returns mock data
- Check ML service logs for errors
- Ensure ML_SERVICE_URL is correct

### Invalid Response

- Backend validates all responses
- Missing fields are filled with defaults
- Invalid categories are mapped to "other"

---

## Performance Optimization

### 1. Model Optimization
- Use quantization to reduce model size
- Optimize inference speed (<3 seconds ideal)
- Consider using ONNX runtime

### 2. Caching
- Cache predictions for identical images
- Use Redis for distributed caching
- Store predictions in database

### 3. Batch Processing
- Process multiple images in parallel
- Use GPU for faster inference
- Consider using TensorFlow Serving

### 4. Load Balancing
- Deploy multiple ML service instances
- Use nginx for load balancing
- Scale horizontally based on traffic

---

## Monitoring

### Metrics to Track

1. **Latency**: Time to process each image
2. **Accuracy**: Compare predictions to user corrections
3. **Confidence**: Average confidence scores
4. **Error Rate**: Failed predictions / total requests
5. **Throughput**: Images processed per second

### Logging

Add logging to your ML service:

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.post("/analyze")
async def analyze_food(request: ImageRequest):
    logger.info(f"Received image for analysis")
    
    # ... inference code ...
    
    logger.info(f"Predicted: {food_name}, Confidence: {confidence}")
    return response
```

---

## Model Updates

### Versioning

Use version in URL:

```env
ML_SERVICE_URL=http://ml-service:5000/api/v1
```

### A/B Testing

Deploy two versions and compare:

```python
# Route 50% to v1, 50% to v2
if random.random() < 0.5:
    response = await call_ml_v1(image)
else:
    response = await call_ml_v2(image)
```

### Gradual Rollout

Start with 10% traffic, increase gradually:

```python
if user_id % 10 == 0:  # 10% of users
    response = await call_new_model(image)
else:
    response = await call_old_model(image)
```

---

## Troubleshooting

### "ML service URL not configured"
**Solution:** Set `ML_SERVICE_URL` in `.env` file

### "ML service timeout"
**Solution:** Optimize model inference or increase timeout in `ml_service.py`

### "Invalid category returned"
**Solution:** Check model output, ensure it returns one of the 6 valid categories

### "Connection refused"
**Solution:** Ensure ML service is running and accessible at the configured URL

### "Low confidence scores"
**Solution:** Improve model training data, retrain model with more examples

---

## Next Steps

1. ✅ Train your food recognition model
2. ✅ Deploy ML service with `/analyze` endpoint
3. ✅ Set `ML_SERVICE_URL` in backend `.env`
4. ✅ Test with sample images
5. ✅ Monitor performance and accuracy
6. ✅ Iterate and improve model

---

## Summary

Your backend is **ready to integrate** with your custom ML model! Just:

1. Deploy your model with the `/analyze` endpoint
2. Set `ML_SERVICE_URL` environment variable
3. Test and monitor

**No code changes needed in the backend!** 🎉

The validation, normalization, and error handling are all built-in.

