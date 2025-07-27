# Running the FastAPI Backend

## 1. Activate the Virtual Environment (if not already active)
You do not need to activate the venv if you use the full path in the next step.

## 2. Start the FastAPI Server using the venv
Run this command from your project root:

```sh
.venv/bin/python -m uvicorn app.main:app --reload
```

This ensures all dependencies are available and the server will auto-reload on code changes.

**Note:**
- If you change environment variables in your `.env` file, you must manually restart the server for changes to take effect.
- For Python code changes, the server will auto-reload if started with `--reload`.
# Travel Site Backend (FastAPI + MongoDB Atlas)

This is the backend for the travel website, built with FastAPI and using MongoDB Atlas as the database.

## API Documentation

### Chatbot Endpoints

#### 1. Generate Travel Plan
Generate a travel itinerary with booking links using AI.

```
POST /chat/
```

**Request Body:**
```json
{
    "message": "string",     // The travel request message
    "user_id": "string"      // Optional: User ID to track chat history
}
```

**Response:**
```json
{
    "summary": "string",     // Brief overview of the trip
    "itinerary": [          // Array of daily activities
        {
            "city": "string",
            "activities": ["string"],
            "accommodation": "string"  // Optional
        }
    ],
    "booking_links": {      // Links for booking
        "booking": "string", // Booking.com link
        "skyscanner": "string" // Skyscanner link
    },
    "cities": ["string"]    // List of unique cities in itinerary
}
```

**Example Request:**
```json
{
    "message": "Plan a 3-day trip to Paris",
    "user_id": "user123"
}
```

#### 2. Get Chat History
Retrieve previous chat interactions for a specific user.

```
GET /chat/history/{user_id}
```

**Path Parameters:**
- `user_id`: String (required) - The ID of the user whose history to retrieve

**Response:**
```json
[
    {
        "id": "string",
        "user_id": "string",
        "request": "string",
        "response": {
            "summary": "string",
            "itinerary": [...],
            "booking_links": {...},
            "cities": [...]
        },
        "created_at": "2025-07-26T10:00:00Z"
    }
]
```

### Error Responses

Both endpoints may return these error responses:

- `400 Bad Request`: Invalid request format
- `404 Not Found`: User ID not found (for history endpoint)
- `500 Internal Server Error`: Server or API errors

In case of errors, the response will have this structure:
```json
{
    "summary": "Error message",
    "itinerary": [],
    "booking_links": {},
    "cities": []
}
```

### Usage Notes

1. The chatbot uses GPT-3.5 to generate detailed travel plans
2. Booking links are automatically generated for each unique city
3. All successful chat interactions are saved to the database
4. Chat history is ordered by most recent first
5. The response includes both accommodation suggestions and daily activities
6. Cities list can be used to show destinations on a map or generate additional booking links

### Frontend Integration Example

```typescript
// Example using fetch API
const generateTravelPlan = async (message: string, userId?: string) => {
  try {
    const response = await fetch('http://your-api-url/chat/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message,
        user_id: userId,
      }),
    });
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error:', error);
    throw error;
  }
};

// Example using axios
const getChatHistory = async (userId: string) => {
  try {
    const response = await axios.get(`http://your-api-url/chat/history/${userId}`);
    return response.data;
  } catch (error) {
    console.error('Error:', error);
    throw error;
  }
};
```

## Features
- User authentication (direct, Google, Facebook)
- CRUD for trips (past/future)
- Enquiries/suggestions
- Chatbot integration (OpenAI, bookings.com, Skyscanner)
- Itinerary PDF generation
- Search history

## Setup
1. Create a virtual environment:
   ```sh
   python3 -m venv venv
   source venv/bin/activate
   ```
2. Install dependencies:
   ```sh
   pip install fastapi uvicorn motor pymongo python-jose[cryptography] passlib[bcrypt] python-dotenv requests
   ```
3. Create a `.env` file with your MongoDB Atlas URI and any API keys needed.
4. Run the server:
   ```sh
   uvicorn app.main:app --reload
   ```

## Project Structure
- `app/main.py`: FastAPI entrypoint
- `app/api/`: API routers (trips, auth, chatbot, etc.)
- `app/models/`: Pydantic models
- `app/db/`: Database connection and helpers
- `app/utils/`: Utility functions (PDF, OpenAI, etc.)

---
Replace placeholder code and secrets before deploying to production.
# travel-site-back-end
