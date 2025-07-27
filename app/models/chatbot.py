from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Optional
from bson import ObjectId

class User(BaseModel):
    id: str = Field(default_factory=lambda: str(ObjectId()))
    email: str
    name: Optional[str]
    picture: Optional[str]
    auth_provider: str  # 'google', 'facebook', or 'apple'
    provider_user_id: str  # ID from the auth provider
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ChatRequest(BaseModel):
    message: str
    user_id: Optional[str] = None  # To track which user made the request

class ItineraryDay(BaseModel):
    city: str
    activities: List[str]
    accommodation: Optional[str]

class ChatResponse(BaseModel):
    summary: str
    itinerary: List[ItineraryDay]
    booking_links: dict  # Will contain generated booking.com and skyscanner links
    cities: List[str]  # List of unique cities in the itinerary

class ChatHistory(BaseModel):
    id: str = Field(default_factory=lambda: str(ObjectId()))
    user_id: Optional[str]
    request: str
    response: ChatResponse
    created_at: datetime = Field(default_factory=datetime.utcnow)
