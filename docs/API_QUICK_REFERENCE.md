# API Quick Reference - Weight Goals & Vision

## Base URL
```
http://localhost:8000
```

---

## Weight Goals Endpoints

### 1. Create/Update Goal
```http
POST /api/goals?user_id={uuid}
Content-Type: application/json

{
  "goal_type": "lose_weight",  // or: gain_weight, maintain, diabetes_management
  "target_calories": 1650      // optional
}
```

**Response:**
```json
{
  "id": "goal-uuid",
  "user_id": "user-uuid",
  "goal_type": "lose_weight",
  "target_calories": 1650,
  "is_active": true,
  "created_at": "2025-10-18T12:00:00"
}
```

### 2. Get User's Goal
```http
GET /api/goals?user_id={uuid}
```

**Response:**
```json
{
  "id": "goal-uuid",
  "user_id": "user-uuid",
  "goal_type": "lose_weight",
  "target_calories": 1650,
  "is_active": true,
  "created_at": "2025-10-18T12:00:00"
}
```

### 3. Get Recommendations
```http
GET /api/goals/recommendations?goal_type=lose_weight
```

**Response:**
```json
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
  "tips": "Focus on nutrient-dense, low-calorie foods..."
}
```

### 4. Calculate Target Calories
```http
POST /api/goals/calculate-calories?user_id={uuid}&current_weight=70&height=170&age=25&activity_level=moderate
```

**Query Parameters:**
- `user_id` (required): User UUID
- `current_weight` (optional): Weight in kg
- `height` (optional): Height in cm
- `age` (optional): Age in years
- `activity_level` (optional): sedentary, light, moderate, active, very_active

**Response:**
```json
{
  "user_id": "user-uuid",
  "target_calories": 1847,
  "activity_level": "moderate"
}
```

---

## Food Upload (Vision API)

### Upload Food Image
```http
POST /api/food/upload
Content-Type: multipart/form-data

- image: File (required)
- user_id: string (optional)
- meal_type: string (optional: breakfast, lunch, dinner, snack)
```

**Example using cURL:**
```bash
curl -X POST "http://localhost:8000/api/food/upload" \
  -F "image=@/path/to/food.jpg" \
  -F "user_id=123e4567-e89b-12d3-a456-426614174000" \
  -F "meal_type=lunch"
```

**Response:**
```json
{
  "log_id": "log-uuid",
  "image_url": "https://supabase.co/.../food.jpg",
  "detected_food_name": "Grilled Chicken Breast",
  "food_category": "protein",
  "healthiness_score": 88,
  "calories": 165,
  "meal_type": "lunch",
  "confidence": 0.94,
  "message": "Food image uploaded and analyzed successfully"
}
```

**Food Categories:**
- `fruit` - All fruits (apples, bananas, berries, etc.)
- `vegetable` - All vegetables (broccoli, carrots, salads, etc.)
- `protein` - Meat, fish, eggs, tofu, beans, nuts
- `dairy` - Milk, cheese, yogurt, ice cream
- `grain` - Bread, rice, pasta, cereals, oats
- `other` - Processed foods, desserts, drinks, mixed dishes

**Healthiness Score:**
- 90-100: Very healthy (raw fruits, vegetables, lean protein)
- 70-89: Healthy (whole grains, dairy, cooked vegetables)
- 50-69: Moderate (mixed dishes, some processed foods)
- 30-49: Less healthy (fried foods, high sugar/fat)
- 0-29: Unhealthy (junk food, highly processed)

---

## Chatbot (Enhanced with Goals)

### Chat with AI
```http
POST /api/chatbot/chat
Content-Type: application/json

{
  "user_id": "user-uuid",  // optional, for personalized advice
  "message": "What should I eat next?",
  "include_context": true  // optional, default: true
}
```

**Response:**
```json
{
  "response": "You have 1000 calories remaining for your weight loss goal. Add dairy to complete all food groups. Try Greek yogurt or cottage cheese for high protein and low calories."
}
```

### Quick Actions

**Missing Food Groups:**
```http
POST /api/chatbot/missing-groups
{
  "user_id": "user-uuid"
}
```

**Meal Suggestions:**
```http
POST /api/chatbot/meal-suggestions
{
  "user_id": "user-uuid"
}
```

**Nutrition Tips:**
```http
POST /api/chatbot/nutrition-tips
{
  "user_id": "user-uuid"
}
```

---

## Example Workflows

### Workflow 1: New User Setup

```bash
# 1. Create user (assume user_id is created)
USER_ID="123e4567-e89b-12d3-a456-426614174000"

# 2. Set weight loss goal
curl -X POST "http://localhost:8000/api/goals?user_id=$USER_ID" \
  -H "Content-Type: application/json" \
  -d '{"goal_type": "lose_weight"}'

# 3. Calculate personalized calories
curl -X POST "http://localhost:8000/api/goals/calculate-calories?user_id=$USER_ID&current_weight=80&height=175&age=28&activity_level=moderate"

# 4. Get recommendations
curl "http://localhost:8000/api/goals/recommendations?goal_type=lose_weight"
```

### Workflow 2: Daily Food Logging

```bash
USER_ID="123e4567-e89b-12d3-a456-426614174000"

# 1. Upload breakfast
curl -X POST "http://localhost:8000/api/food/upload" \
  -F "image=@breakfast.jpg" \
  -F "user_id=$USER_ID" \
  -F "meal_type=breakfast"

# 2. Upload lunch
curl -X POST "http://localhost:8000/api/food/upload" \
  -F "image=@lunch.jpg" \
  -F "user_id=$USER_ID" \
  -F "meal_type=lunch"

# 3. Ask chatbot for advice
curl -X POST "http://localhost:8000/api/chatbot/chat" \
  -H "Content-Type: application/json" \
  -d "{\"user_id\": \"$USER_ID\", \"message\": \"What should I eat for dinner?\"}"
```

### Workflow 3: Check Progress

```bash
USER_ID="123e4567-e89b-12d3-a456-426614174000"

# 1. Get today's logs
curl "http://localhost:8000/api/food/logs?user_id=$USER_ID&start_date=2025-10-18&end_date=2025-10-18"

# 2. Get current goal
curl "http://localhost:8000/api/goals?user_id=$USER_ID"

# 3. Ask chatbot for summary
curl -X POST "http://localhost:8000/api/chatbot/chat" \
  -H "Content-Type: application/json" \
  -d "{\"user_id\": \"$USER_ID\", \"message\": \"How am I doing today?\"}"
```

---

## Testing in Swagger UI

Visit: `http://localhost:8000/docs`

### Test Goal Creation
1. Expand `POST /api/goals`
2. Click "Try it out"
3. Enter `user_id` in query parameter
4. Enter request body:
   ```json
   {
     "goal_type": "lose_weight",
     "target_calories": 1650
   }
   ```
5. Click "Execute"

### Test Food Upload
1. Expand `POST /api/food/upload`
2. Click "Try it out"
3. Upload an image file
4. Enter `user_id` and `meal_type`
5. Click "Execute"
6. See AI analysis results!

### Test Chatbot
1. Expand `POST /api/chatbot/chat`
2. Click "Try it out"
3. Enter request body:
   ```json
   {
     "user_id": "your-uuid",
     "message": "What should I eat next?",
     "include_context": true
   }
   ```
4. Click "Execute"
5. See personalized advice!

---

## Goal Types & Personalization

### lose_weight
- **Calories**: 1,500-1,800/day (-20% deficit)
- **Macros**: 30-35% protein, 35-40% carbs, 25-30% fat
- **Priority**: vegetables, protein, fruit
- **Advice**: High protein, plenty of veggies, portion control

### gain_weight
- **Calories**: 2,500-3,000/day (+20% surplus)
- **Macros**: 25-30% protein, 45-50% carbs, 25-30% fat
- **Priority**: protein, grain, dairy
- **Advice**: Calorie-dense foods, frequent meals, protein shakes

### maintain
- **Calories**: 2,000-2,200/day (maintenance)
- **Macros**: 20-25% protein, 45-50% carbs, 25-30% fat
- **Priority**: balanced (all groups)
- **Advice**: Balanced nutrition, all food groups daily

### diabetes_management
- **Calories**: 1,800-2,200/day (maintenance)
- **Macros**: 25-30% protein, 40-45% carbs, 25-30% fat
- **Priority**: vegetable, protein, grain
- **Advice**: Low glycemic foods, carb monitoring, fiber

---

## Error Handling

### Common Error Responses

**400 Bad Request:**
```json
{
  "detail": "Invalid goal_type. Must be one of: maintain, lose_weight, gain_weight, diabetes_management"
}
```

**404 Not Found:**
```json
{
  "detail": "User not found"
}
```

**500 Internal Server Error:**
```json
{
  "detail": "Failed to upload and analyze food image: ..."
}
```

---

## Performance Notes

### Vision API
- **Latency**: 2-5 seconds for image analysis
- **Timeout**: 30 seconds
- **Fallback**: Automatic fallback to mock data if fails

### Goal Calculations
- **Latency**: <100ms
- **Caching**: Goals cached in database
- **Real-time**: Advice calculated on-demand

### Chatbot
- **Latency**: 1-3 seconds for responses
- **Context**: Fetches user data, goals, and food logs
- **Personalized**: Every response tailored to user's goal

---

## Frontend Integration Tips

### For Food Upload Screen
```typescript
async function uploadFood(imageFile: File, userId: string, mealType: string) {
  const formData = new FormData();
  formData.append('image', imageFile);
  formData.append('user_id', userId);
  formData.append('meal_type', mealType);
  
  const response = await fetch('http://localhost:8000/api/food/upload', {
    method: 'POST',
    body: formData
  });
  
  const result = await response.json();
  
  // Display results:
  // - result.detected_food_name
  // - result.food_category
  // - result.healthiness_score
  // - result.calories
  
  return result;
}
```

### For Goal Setting Screen
```typescript
async function setGoal(userId: string, goalType: string, targetCalories?: number) {
  const response = await fetch(`http://localhost:8000/api/goals?user_id=${userId}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      goal_type: goalType,
      target_calories: targetCalories
    })
  });
  
  return await response.json();
}

async function getRecommendations(goalType: string) {
  const response = await fetch(
    `http://localhost:8000/api/goals/recommendations?goal_type=${goalType}`
  );
  return await response.json();
}
```

### For Chatbot
```typescript
async function chat(userId: string, message: string) {
  const response = await fetch('http://localhost:8000/api/chatbot/chat', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      user_id: userId,
      message: message,
      include_context: true
    })
  });
  
  const result = await response.json();
  return result.response;  // The chatbot's text response
}
```

---

## Summary

✅ **All endpoints are ready and working**
✅ **Gemini Vision AI integrated for food recognition**
✅ **4 goal types with personalized recommendations**
✅ **Chatbot enhanced with goal-aware advice**
✅ **Full documentation and examples provided**

**Start testing at:** http://localhost:8000/docs

