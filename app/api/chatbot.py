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
You are a travel planning assistant. Create a detailed travel itinerary following this exact format:

Travel Itinerary

Trip Summary:
[2-3 sentences describing the overall trip]

Daily Itinerary:
Day 1 - [City/Location]
• [Activity 1]
• [Activity 2]
• [Activity 3]
[Accommodation details if changing location]

Day 2 - [City/Location]
[Continue format for each day]

Important formatting rules:
1. Start each day with "Day X - [Location]"
2. List activities with bullet points (•)
3. Include accommodation only when changing locations
4. Keep descriptions concise and practical

User's message: {user_message}
"""

def extract_cities(itinerary: List[ItineraryDay]) -> List[str]:
    """Extract and return unique cities from itinerary"""
    cities = [day.city for day in itinerary]
    return list(dict.fromkeys(cities))  # Remove duplicates while preserving order

def generate_booking_links(itinerary: List[ItineraryDay]) -> Dict[str, str]:
    """Generate booking.com and skyscanner links based on the itinerary"""
    if not itinerary:
        return {"booking": "", "skyscanner": ""}
        
    cities = extract_cities(itinerary)
    if not cities:
        return {"booking": "", "skyscanner": ""}
        
    total_days = len(itinerary)
    main_city = cities[0].split()[0]  # Take first word of city name for better compatibility
    
    # Generate Booking.com link
    booking_url = (
        f"https://www.booking.com/searchresults.html"
        f"?ss={main_city.replace(' ', '+')}"
        f"&checkin=flexible"
        f"&group_adults=2"
        f"&no_rooms=1"
        f"&group_children=0"
        f"&nflt=ht_id%3D204"  # Filter for hotels
    )
    
    # Generate Skyscanner link
    city_code = main_city[:3].upper()
    skyscanner_url = f"https://www.skyscanner.com/transport/flights/{city_code}"
    
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
    # Extract summary
    summary_match = re.search(r'Trip Summary:(.+?)(?=Day \d|$)', response_text, re.DOTALL)
    if not summary_match:
        raise ValueError("Could not find Trip Summary section")
    summary_section = summary_match.group(1).strip()
    
    # Extract and parse daily itinerary
    itinerary_days = []
    day_sections = re.findall(r'Day (\d+)[^\n]*?(?:\n|$)(?:(?!Day \d).)*', response_text, re.DOTALL)
    
    current_section = None
    for section in re.split(r'(Day \d+[^\n]*)', response_text):
        section = section.strip()
        if not section:
            continue
            
        if section.startswith('Day'):
            if current_section:
                # Parse previous section
                city = current_section['heading'].split(' - ')[-1].strip()
                activities = [a.strip('• ').strip() for a in current_section['content']]
                accommodation = next((a for a in activities if 'stay' in a.lower() or 'resort' in a.lower() or 'hotel' in a.lower() or 'accommodation' in a.lower()), None)
                if accommodation:
                    activities.remove(accommodation)
                
                itinerary_days.append(ItineraryDay(
                    city=city,
                    activities=activities,
                    accommodation=accommodation
                ))
                
            current_section = {'heading': section, 'content': []}
        elif current_section is not None:
            current_section['content'].extend([l.strip() for l in section.split('\n') if l.strip() and not l.strip().startswith('Day')])
    
    # Don't forget to add the last section
    if current_section:
        city = current_section['heading'].split(' - ')[-1].strip()
        activities = [a.strip('• ').strip() for a in current_section['content']]
        accommodation = next((a for a in activities if 'stay' in a.lower() or 'resort' in a.lower() or 'hotel' in a.lower() or 'accommodation' in a.lower()), None)
        if accommodation:
            activities.remove(accommodation)
        
        itinerary_days.append(ItineraryDay(
            city=city,
            activities=activities,
            accommodation=accommodation
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
