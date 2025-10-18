# Weight Goals & Vision API Features

## Overview

This document describes two major features implemented in the backend:

1. **Weight Goal Personalization** - Personalized nutrition recommendations based on user goals
2. **Gemini Vision API Integration** - AI-powered food recognition from photos

---

## Feature 1: Weight Goal Personalization

### What It Does

Provides personalized nutrition advice based on user's weight goals:
- **Weight Loss**: High protein, vegetables, low calories (1,500-1,800 cal/day)
- **Weight Gain**: Calorie-dense foods, protein, complex carbs (2,500-3,000 cal/day)
- **Maintenance**: Balanced nutrition from all food groups (2,000-2,200 cal/day)
- **Diabetes Management**: Low glycemic foods, fiber, carb monitoring (1,800-2,200 cal/day)

### Backend Architecture

#### 1. Goal Service (`services/goal_service.py`)

Core service handling goal logic:

**Key Methods:**
- `create_or_update_goal(user_id, goal_type, target_calories)` - Create/update user goals
- `get_active_goal(user_id)` - Retrieve user's active goal
- `get_nutrition_recommendations(goal_type)` - Get personalized recommendations
- `get_personalized_advice(user_id, current_calories, food_groups_eaten)` - Real-time advice
- `calculate_target_calories(user_id, weight, height, age, activity_level)` - Calculate daily calorie target using Harris-Benedict equation

**Personalization Details:**

Each goal type includes:
- Daily calorie targets
- Macronutrient ratios (protein/carbs/fat %)
- Priority food groups
- Calorie modifiers (+20% for gain, -20% for loss)
- Specific tips and focus areas

#### 2. Goal Routes (`routes/goals.py`)

**Endpoints:**

```python
# Create or update user goal
POST /api/goals?user_id={uuid}
Body: {
  "goal_type": "lose_weight",  # or gain_weight, maintain, diabetes_management
  "target_calories": 1650      # optional
}

# Get user's active goal
GET /api/goals?user_id={uuid}

# Get recommendations for a goal type
GET /api/goals/recommendations?goal_type=lose_weight

# Calculate personalized calorie target
POST /api/goals/calculate-calories?user_id={uuid}&current_weight=70&height=170&age=25&activity_level=moderate
```

#### 3. Chatbot Integration

The chatbot now includes goal information in user context:

**Updated Context Includes:**
- User's current goal (Weight Loss, Gain, Maintenance, Diabetes)
- Target daily calories
- Calories remaining today
- Personalized advice based on goal and current intake

**Example Enhanced Context:**
```
Today's nutrition data:
- Meals logged: 3
- Categories: Fruits (1), Vegetables (2), Protein (2), Dairy (0), Grains (1)
- Total calories: 650
- Missing groups: Dairy
- Current streak: 5 days
- Goal: Weight Loss
- Target calories: 1650
- Calories remaining: 1000
- Goal advice: For weight loss, prioritize dairy.
- Recent meals: Apple, Chicken breast, Salad
```

**Updated System Prompt:**
- Personalizes advice based on goal type
- For weight loss: emphasizes protein, vegetables, calorie targets
- For weight gain: emphasizes calorie-dense foods, meeting targets
- For diabetes: emphasizes low glycemic foods, carb monitoring

### Personalization Examples

#### Weight Loss
- **Focus**: Vegetables (unlimited), lean protein, moderate fruits
- **Macros**: 30-35% protein, 35-40% carbs, 25-30% fat
- **Tips**: "Focus on nutrient-dense, low-calorie foods. Stay full with protein and vegetables."
- **Priority Groups**: vegetable, protein, fruit

#### Weight Gain
- **Focus**: Protein shakes, complex carbs, healthy fats, frequent meals
- **Macros**: 25-30% protein, 45-50% carbs, 25-30% fat
- **Tips**: "Eat calorie-dense foods. Don't skip meals. Add healthy fats."
- **Priority Groups**: protein, grain, dairy

#### Diabetes Management
- **Focus**: Low glycemic foods, high fiber, lean protein, whole grains
- **Macros**: 25-30% protein, 40-45% carbs, 25-30% fat
- **Tips**: "Monitor carbs carefully. Choose complex carbs. Eat regular meals."
- **Priority Groups**: vegetable, protein, grain

---

## Feature 2: Gemini Vision API Integration

### What It Does

Uses Google's Gemini Vision AI to automatically recognize food from photos and determine:
- Food name (e.g., "Grilled Chicken Breast")
- Food category (fruit, vegetable, protein, dairy, grain, other)
- Healthiness score (0-100)
- Estimated calories
- Confidence level

### How It Works

#### 1. Enhanced ML Service (`services/ml_service.py`)

**Primary Method: Gemini Vision API**
- Uses `gemini-1.5-flash` model for image analysis
- Processes images with detailed prompt instructions
- Returns structured JSON response

**Fallback Chain:**
1. **Gemini Vision** (primary) - Google's multimodal AI
2. **External ML Service** (if configured) - Custom ML endpoint
3. **Mock Response** (development) - Sample data for testing

**Vision Analysis Prompt:**
```
Analyze this food image and provide JSON with:
- food_name: specific name
- category: fruit/vegetable/protein/dairy/grain/other
- healthiness_score: 0-100
- calories: estimated per serving
- confidence: 0.0-1.0
- description: brief description

Healthiness scoring:
- 90-100: Very healthy (raw fruits, vegetables, lean protein)
- 70-89: Healthy (whole grains, dairy, cooked veggies)
- 50-69: Moderate (mixed dishes, some processed)
- 30-49: Less healthy (fried, high sugar/fat)
- 0-29: Unhealthy (junk food, highly processed)
```

**Category Validation:**
- Normalizes category names (e.g., "vegetables" → "vegetable")
- Maps variations (e.g., "meat" → "protein", "carbs" → "grain")
- Validates against allowed categories

#### 2. Food Upload Flow

**Existing Endpoint:**
```python
POST /api/food/upload
Content-Type: multipart/form-data

Parameters:
- image: File (required)
- user_id: string (optional, for anonymous users)
- meal_type: string (optional: breakfast, lunch, dinner, snack)
```

**Processing Steps:**
1. Upload image to Supabase Storage (`storage_service`)
2. Convert image to base64
3. Analyze with Gemini Vision (`ml_service.analyze_food_image()`)
4. Create food log entry in database (`food_service.create_food_log()`)
5. Update daily nutrition summary (if authenticated)
6. Return analysis results

**Response:**
```json
{
  "log_id": "uuid",
  "image_url": "https://...",
  "detected_food_name": "Grilled Chicken Breast",
  "food_category": "protein",
  "healthiness_score": 85,
  "calories": 165,
  "meal_type": "lunch",
  "confidence": 0.94,
  "message": "Food image uploaded and analyzed successfully"
}
```

### Gemini Vision Features

#### Accurate Food Recognition
- Identifies specific foods (not just categories)
- Handles complex dishes and mixed foods
- Provides confidence scores

#### Smart Categorization
- Follows predefined category rules
- Prioritizes main ingredient for mixed dishes
- Maps to 5 core food groups + "other"

#### Healthiness Scoring
- Considers preparation method (raw vs. fried)
- Evaluates nutritional density
- Accounts for processing level

#### Calorie Estimation
- Based on typical serving sizes
- Considers preparation methods
- Provides reasonable estimates

### Integration with Food Tracking

The Vision API seamlessly integrates with existing features:

1. **Food Logs** - Automatically creates entries with ML data
2. **Daily Summary** - Updates category counts after each upload
3. **Streaks** - Contributes to daily completion
4. **Chatbot** - Uses recognized foods for personalized advice
5. **Analytics** - Provides data for nutrition insights

---

## Database Schema

### user_goals Table

```sql
CREATE TABLE user_goals (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(id),
  goal_type TEXT NOT NULL,  -- 'maintain', 'lose_weight', 'gain_weight', 'diabetes_management'
  target_calories INTEGER,
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT NOW()
);
```

### food_logs Table (Enhanced)

Already exists, used by Vision API:

```sql
CREATE TABLE food_logs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(id),
  image_url TEXT NOT NULL,
  detected_food_name TEXT NOT NULL,
  food_category TEXT NOT NULL,  -- Set by Gemini Vision
  healthiness_score INTEGER NOT NULL,  -- Set by Gemini Vision
  calories INTEGER,  -- Set by Gemini Vision
  meal_type TEXT,
  logged_at TIMESTAMP DEFAULT NOW(),
  created_at TIMESTAMP DEFAULT NOW()
);
```

---

## Usage Examples

### Example 1: Setting a Weight Loss Goal

```bash
# Create weight loss goal
curl -X POST "http://localhost:8000/api/goals?user_id=123e4567-e89b-12d3-a456-426614174000" \
  -H "Content-Type: application/json" \
  -d '{
    "goal_type": "lose_weight",
    "target_calories": 1650
  }'

# Get personalized recommendations
curl "http://localhost:8000/api/goals/recommendations?goal_type=lose_weight"

# Response:
{
  "title": "Weight Loss Plan",
  "daily_calories": "1,500-1,800 calories",
  "focus": [
    "High protein intake (lean meats, fish, eggs)",
    "Plenty of vegetables and leafy greens",
    "Moderate fruits (2-3 servings)",
    "Whole grains in small portions",
    "Low-fat dairy products"
  ],
  "tips": "Focus on nutrient-dense, low-calorie foods. Prioritize vegetables and lean protein..."
}
```

### Example 2: Uploading Food with Vision API

```bash
# Upload food image
curl -X POST "http://localhost:8000/api/food/upload" \
  -F "image=@chicken_breast.jpg" \
  -F "user_id=123e4567-e89b-12d3-a456-426614174000" \
  -F "meal_type=lunch"

# Response (Gemini Vision analysis):
{
  "log_id": "abc123...",
  "image_url": "https://supabase.../chicken_breast.jpg",
  "detected_food_name": "Grilled Chicken Breast",
  "food_category": "protein",
  "healthiness_score": 88,
  "calories": 165,
  "meal_type": "lunch",
  "confidence": 0.94,
  "message": "Food image uploaded and analyzed successfully"
}
```

### Example 3: Chatbot with Goal Context

```bash
# Ask chatbot for advice (user has weight loss goal)
curl -X POST "http://localhost:8000/api/chatbot/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "123e4567-e89b-12d3-a456-426614174000",
    "message": "What should I eat next?"
  }'

# Response (personalized for weight loss):
{
  "response": "You have 1000 calories remaining for your weight loss goal. Add dairy to complete all food groups. Try Greek yogurt or cottage cheese for high protein and low calories."
}
```

---

## Testing the Features

### Test Goal Endpoints

```bash
# 1. Create weight gain goal
POST /api/goals?user_id={your_uuid}
{
  "goal_type": "gain_weight"
}

# 2. Calculate personalized calories
POST /api/goals/calculate-calories?user_id={uuid}&current_weight=65&height=175&age=22&activity_level=active

# 3. Get goal
GET /api/goals?user_id={uuid}
```

### Test Vision API

```bash
# 1. Upload an apple photo
POST /api/food/upload
- Select apple.jpg
- user_id: {uuid}
- meal_type: snack

# Expected: food_name: "Apple", category: "fruit", healthiness_score: 90+

# 2. Upload a pizza photo
POST /api/food/upload
- Select pizza.jpg
- user_id: {uuid}
- meal_type: dinner

# Expected: food_name: "Pizza", category: "other", healthiness_score: 30-50

# 3. Upload vegetables
POST /api/food/upload
- Select salad.jpg
- user_id: {uuid}

# Expected: category: "vegetable", healthiness_score: 85+
```

### Test Chatbot Integration

```bash
# 1. Set a weight loss goal
# 2. Log some foods
# 3. Ask chatbot: "What should I eat next?"
# Expected: Goal-specific advice about remaining calories and missing food groups

# 4. Ask: "How am I doing with my goal?"
# Expected: Assessment of progress toward goal
```

---

## Configuration

### Environment Variables

```env
# Required for Gemini Vision API
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-pro  # Used for chatbot

# Optional: External ML service (fallback)
ML_SERVICE_URL=http://your-ml-service.com
```

### Gemini Vision Model

Currently using: `gemini-1.5-flash`
- Fast inference
- Good accuracy for food recognition
- Cost-effective
- Multimodal (image + text)

---

## Benefits

### For Users

1. **Personalized Nutrition** - Advice tailored to individual goals
2. **Automatic Tracking** - Just take a photo, AI does the rest
3. **Accurate Recognition** - Gemini Vision identifies foods accurately
4. **Goal Progress** - Real-time feedback on calorie and nutrition targets
5. **Smart Recommendations** - Chatbot considers goals when suggesting foods

### For Developers

1. **No Custom ML Training** - Uses Google's pre-trained models
2. **Easy Integration** - Simple API calls
3. **Fallback Chain** - Robust error handling
4. **Extensible** - Can add custom ML models later
5. **Well Documented** - Clear code and comments

---

## Next Steps / Future Enhancements

### Potential Improvements

1. **Portion Size Detection** - Estimate serving sizes from images
2. **Multiple Foods** - Detect multiple items in one photo
3. **Meal Tracking** - Group foods into complete meals
4. **Recipe Analysis** - Recognize homemade dishes
5. **Barcode Scanning** - Supplement vision with nutrition labels
6. **Goal Progress Visualization** - Charts showing progress toward goals
7. **Adaptive Goals** - Auto-adjust targets based on progress
8. **Meal Planning** - Suggest meals that align with goals

### Database Enhancements

1. Add `portion_size` field to food_logs
2. Create `meal_plans` table
3. Add `weekly_goals` and `monthly_goals` tracking
4. Store user preferences for food recommendations

---

## Troubleshooting

### Common Issues

#### Gemini Vision Errors

**Issue**: "Failed to parse Gemini Vision JSON response"
- **Cause**: Model returned non-JSON text
- **Solution**: Check prompt formatting, verify API key

**Issue**: "Gemini Vision timeout"
- **Cause**: Large image or API throttling
- **Solution**: Falls back to external service or mock data automatically

#### Goal Service Errors

**Issue**: "No active goal found"
- **Cause**: User hasn't set a goal yet
- **Solution**: Create a goal first or use default "maintain"

**Issue**: "Failed to calculate calories"
- **Cause**: Missing user data (weight, height, age)
- **Solution**: Use goal-based defaults or prompt user for info

### Debug Mode

Enable detailed logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## API Documentation

Full API documentation available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

All endpoints are fully documented with:
- Request parameters
- Request body schemas
- Response schemas
- Example requests/responses

---

## Files Modified/Created

### Created
- `backend/services/goal_service.py` - Goal management service
- `docs/WEIGHT_GOALS_AND_VISION_API.md` - This documentation

### Modified
- `backend/routes/goals.py` - Implemented all goal endpoints
- `backend/services/chatbot_service.py` - Added goal context and personalization
- `backend/services/ml_service.py` - Integrated Gemini Vision API
- `backend/schemas/goal_schemas.py` - Already had schemas (no changes needed)
- `backend/models/goal.py` - Already had models (no changes needed)

### Unchanged (Already Working)
- `backend/routes/food.py` - Upload endpoint already exists
- `backend/services/food_service.py` - Food logging already works
- `backend/services/storage_service.py` - Image storage already works

---

## Summary

Both features are now **fully implemented and integrated**:

✅ **Weight Goal Personalization**
- Create/update/get user goals
- Personalized nutrition recommendations for 4 goal types
- Integrated into chatbot for real-time advice
- Calorie calculation using Harris-Benedict equation

✅ **Gemini Vision API Integration**
- AI-powered food recognition from photos
- Automatic categorization and healthiness scoring
- Calorie estimation
- Seamless integration with existing food tracking

**The backend is ready for frontend integration!**

