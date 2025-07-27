from fastapi import APIRouter, HTTPException
import os
import re
from typing import List, Dict, Tuple
from datetime import datetime
from openai import AsyncOpenAI
from dotenv import load_dotenv
from app.models.chatbot import ChatRequest, ChatResponse, ItineraryDay, ChatHistory
from app.db.mongo import db

load_dotenv()

router = APIRouter()

# Initialize MongoDB collection
chat_history = db.chat_history

@router.get("/history/{user_id}", response_model=List[ChatHistory])
async def get_chat_history(user_id: str):
    """Retrieve chat history for a specific user"""
    cursor = chat_history.find({"user_id": user_id}).sort("created_at", -1)
    history = await cursor.to_list(length=None)
    return [ChatHistory(**item) for item in history]

# Initialize OpenAI client
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Travel assistant prompt template
TRAVEL_ASSISTANT_PROMPT = """
You are a travel planning assistant. Please provide a travel plan in the following format:

SUMMARY:
Provide a brief 2-3 sentence overview of the trip.

ITINERARY:
For each day, list:
- City
- Activities (bullet points)
- Accommodation suggestion (if changing locations)

Format the response exactly as shown above, making it easy to parse programmatically.
Keep activities concise and practical.

User's message: {user_message}

Remember to maintain the exact format: SUMMARY section followed by ITINERARY section.
"""

def extract_cities(itinerary: List[ItineraryDay]) -> List[str]:
    """Extract and return unique cities from itinerary"""
    cities = [day.city for day in itinerary]
    return list(dict.fromkeys(cities))  # Remove duplicates while preserving order

def generate_booking_links(itinerary: List[ItineraryDay]) -> Dict[str, str]:
    """Generate booking.com and skyscanner links based on the itinerary"""
    cities = extract_cities(itinerary)
    total_days = len(itinerary)
    
    # Generate Booking.com link for the first city (main destination)
    booking_params = {
        "city": cities[0].replace(" ", "+"),
        "checkin": "flexible",
        "nights": str(total_days)
    }
    booking_url = f"https://www.booking.com/searchresults.html?ss={booking_params['city']}&checkin={booking_params['checkin']}&group_adults=2&no_rooms=1&group_children=0"
    
    # Generate Skyscanner link for the first city
    skyscanner_url = f"https://www.skyscanner.com/transport/flights/{cities[0][:3].upper()}"
    
    return {
        "booking": booking_url,
        "skyscanner": skyscanner_url
    }

async def save_chat_history(request: ChatRequest, response: ChatResponse) -> None:
    """Save chat request and response to MongoDB"""
    history = ChatHistory(
        user_id=request.user_id,
        request=request.message,
        response=response
    )
    await chat_history.insert_one(history.dict())

def parse_ai_response(response_text: str) -> Tuple[str, List[ItineraryDay]]:
    """Parse the AI response into summary and itinerary sections"""
    # Split into summary and itinerary sections
    sections = response_text.split("ITINERARY:")
    if len(sections) != 2:
        raise ValueError("Invalid response format")
    
    summary_section = sections[0].replace("SUMMARY:", "").strip()
    itinerary_section = sections[1].strip()
    
    # Parse itinerary days
    current_city = ""
    current_activities = []
    current_accommodation = None
    itinerary_days = []
    
    for line in itinerary_section.split("\n"):
        line = line.strip()
        if not line:
            continue
            
        # If line starts with "Day" or has a city name
        if line.startswith("Day") or ":" in line:
            # Save previous day if we have one
            if current_city:
                itinerary_days.append(ItineraryDay(
                    city=current_city,
                    activities=current_activities,
                    accommodation=current_accommodation
                ))
            # Reset for new day
            current_city = line.split(":")[-1].strip() if ":" in line else ""
            current_activities = []
            current_accommodation = None
        elif line.startswith("-"):
            activity = line[1:].strip()
            if "accommodation" in activity.lower():
                current_accommodation = activity
            else:
                current_activities.append(activity)
    
    # Add the last day
    if current_city:
        itinerary_days.append(ItineraryDay(
            city=current_city,
            activities=current_activities,
            accommodation=current_accommodation
        ))
    
    return summary_section, itinerary_days

@router.post("/", response_model=ChatResponse)
async def ask_chatbot(request: ChatRequest):
    """Handle chatbot requests and return structured travel responses"""
    try:
        # Check if OpenAI API key is configured
        if not os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY") == "your_openai_key":
            return ChatResponse(
                summary="API Configuration Error",
                itinerary=[],
                booking_links={},
                cities=[]
            )
        
        # Create the prompt with user message
        prompt = TRAVEL_ASSISTANT_PROMPT.format(user_message=request.message)
        
        # Make OpenAI API call
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful travel assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=800,
            temperature=0.7
        )
        
        # Extract and parse the AI's response
        ai_response = response.choices[0].message.content
        if not ai_response:
            return ChatResponse(
                summary="No response generated",
                itinerary=[],
                booking_links={},
                cities=[]
            )
        ai_response = ai_response.strip()

        # Parse the response into structured format
        summary, itinerary = parse_ai_response(ai_response)
        
        # Extract cities and generate booking links
        cities = extract_cities(itinerary)
        booking_links = generate_booking_links(itinerary)

        # Create the response
        chat_response = ChatResponse(
            summary=summary,
            itinerary=itinerary,
            booking_links=booking_links,
            cities=cities
        )

        # Save to MongoDB
        await save_chat_history(request, chat_response)

        return chat_response
        
    except Exception as e:
        print(f"Error in chatbot: {str(e)}")
        return ChatResponse(
            summary="An error occurred while processing your request",
            itinerary=[],
            booking_links={},
            cities=[]
        )
