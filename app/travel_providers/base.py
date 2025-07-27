from abc import ABC, abstractmethod
from typing import List, Optional
from .schemas import (
    SearchCriteria,
    HotelSearchCriteria,
    CabSearchCriteria,
    FlightResult,
    HotelResult,
    CabResult
)

class TravelProvider(ABC):
    """Base class for all travel providers"""
    
    @abstractmethod
    async def search_flights(self, criteria: SearchCriteria) -> List[FlightResult]:
        """Search for flights based on given criteria"""
        pass
    
    @abstractmethod
    async def search_hotels(self, criteria: HotelSearchCriteria) -> List[HotelResult]:
        """Search for hotels based on given criteria"""
        pass
    
    @abstractmethod
    async def get_price_calendar(self, from_city: str, to_city: str) -> dict:
        """Get price calendar for flexible dates"""
        pass
    
    @abstractmethod
    async def check_availability(self, booking_id: str) -> bool:
        """Check if a particular booking ID is still available"""
        pass

class CabProvider(ABC):
    """Base class for cab providers"""
    
    @abstractmethod
    async def search_cabs(self, criteria: CabSearchCriteria) -> List[CabResult]:
        """Search for cabs based on given criteria"""
        pass
    
    @abstractmethod
    async def get_fare_estimate(self, from_location: str, to_location: str) -> float:
        """Get estimated fare for a trip"""
        pass
