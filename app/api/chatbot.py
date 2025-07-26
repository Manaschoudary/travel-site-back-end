from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

# Initialize OpenAI client
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

# Optimized travel assistant prompt template for structured, API-ready responses
TRAVEL_ASSISTANT_PROMPT = """
You are a travel assistant. The user will describe their trip goals. Analyze the message and suggest a multi-city travel itinerary. The user's latitude and longitude may be provided. Use this information to prioritize destinations and activities that are geographically relevant and convenient.

Return a JSON object with the following fields:
- multi_city (bool): Whether the itinerary includes multiple cities.
- destinations (list of city names as strings): Each city should be clearly named for use with travel APIs.
- duration_days (int): Total trip duration.
- estimated_cost (int): Estimated total cost in USD.
- summary (string): A concise summary of the trip.
- itinerary (list of daily plans): Each item should include day (int), title (string), and activities (list of strings).
- transportation (list of segments): Each segment should include from_city (string), to_city (string), mode_of_transport (string, e.g., flight, train, bus), and estimated_cost (int in USD).

Ensure all city names and transport details are formatted for direct use with travel booking APIs. Keep the output concise, structured, and ready for programmatic use.

User's message: {user_message}
"""

@router.post("/", response_model=ChatResponse)
async def ask_chatbot(request: ChatRequest):
    try:
        # Check if OpenAI API key is configured
        if not os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY") == "your_openai_key":
            return ChatResponse(response="Travel Assistant: I'm currently not configured with an OpenAI API key. Please contact support for assistance with your travel questions!")
        
        # Create the prompt with user message
        prompt = TRAVEL_ASSISTANT_PROMPT.format(user_message=request.message)
        
        # Make OpenAI API call
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful travel assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        ai_response = response.choices[0].message.content
        if ai_response:
            ai_response = ai_response.strip()
        else:
            ai_response = "I'm sorry, I couldn't generate a response. Please try again!"
        return ChatResponse(response=ai_response)
        
    except Exception as e:
        # Fallback response in case of API errors
        return ChatResponse(response=f"Travel Assistant: I'm having trouble connecting right now, but I'd love to help with your travel questions! Please try again in a moment or contact our support team for immediate assistance.")
