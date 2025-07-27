from enum import Enum
from typing import Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class TravelProviderType(str, Enum):
    MMT = "makemytrip"
    CLEARTRIP = "cleartrip"
    EMT = "easemytrip"
    INDIGO = "indigo"
    RIYA = "riya"
    SAVAARI = "savaari"

class SearchCriteria(BaseModel):
    from_city: str
    to_city: str
    departure_date: datetime
    return_date: datetime | None = None
    adults: int = 1
    children: int = 0
    class_type: str = "ECONOMY"
    
class HotelSearchCriteria(BaseModel):
    city: str
    check_in: datetime
    check_out: datetime
    rooms: int = 1
    adults: int = 2
    children: int = 0

class CabSearchCriteria(BaseModel):
    city: str
    pickup_date: datetime
    drop_date: datetime | None = None
    cab_type: str = "ALL"
    
class FlightResult(BaseModel):
    provider: TravelProviderType
    flight_number: str
    airline: str
    departure_time: datetime
    arrival_time: datetime
    price: float
    available_seats: int
    class_type: str
    refundable: bool
    deep_link: str
    provider_data: Dict[str, Any] = Field(default_factory=dict)

class HotelResult(BaseModel):
    provider: TravelProviderType
    hotel_name: str
    location: str
    check_in: datetime
    check_out: datetime
    price_per_night: float
    total_price: float
    room_type: str
    amenities: list[str]
    rating: float
    deep_link: str
    provider_data: Dict[str, Any] = Field(default_factory=dict)

class CabResult(BaseModel):
    provider: TravelProviderType
    cab_type: str
    vehicle_model: str
    price_per_km: float
    total_price: float
    available: bool
    rating: float
    deep_link: str
    provider_data: Dict[str, Any] = Field(default_factory=dict)
