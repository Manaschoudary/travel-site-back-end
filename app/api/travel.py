import os
from fastapi import APIRouter, Query
from datetime import datetime
from typing import List, Optional, Dict
from dotenv import load_dotenv
from app.travel_providers.schemas import (
    SearchCriteria,
    HotelSearchCriteria,
    CabSearchCriteria,
    FlightResult,
    HotelResult,
    CabResult,
    TravelProviderType
)
from app.travel_providers.aggregator import TravelAggregator
from app.travel_providers.makemytrip import MakeMyTripProvider
from app.travel_providers.base import TravelProvider, CabProvider

# Load environment variables
load_dotenv()

router = APIRouter()

class SavaariProvider(CabProvider):
    """Savaari implementation of CabProvider"""
    def __init__(self, api_key: str, api_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret

    async def search_cabs(self, criteria: CabSearchCriteria) -> List[CabResult]:
        # Implement Savaari API integration here
        return []

    async def get_fare_estimate(self, from_location: str, to_location: str) -> float:
        # Implement fare estimation here
        return 0.0

class CleartripProvider(TravelProvider):
    """Cleartrip implementation"""
    def __init__(self, api_key: str, api_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret

    async def search_flights(self, criteria: SearchCriteria) -> List[FlightResult]:
        # Implement Cleartrip flight search
        return []

    async def search_hotels(self, criteria: HotelSearchCriteria) -> List[HotelResult]:
        # Implement Cleartrip hotel search
        return []

    async def get_price_calendar(self, from_city: str, to_city: str) -> dict:
        return {}

    async def check_availability(self, booking_id: str) -> bool:
        return True

# Import all providers
from app.travel_providers.easemytrip import EaseMyTripProvider
from app.travel_providers.indigo import IndigoProvider
from app.travel_providers.riya import RiyaTravelProvider

# Initialize providers with credentials from environment variables
mmt_provider = MakeMyTripProvider(
    api_key=os.getenv("MMT_API_KEY", ""),
    api_secret=os.getenv("MMT_API_SECRET", "")
)

cleartrip_provider = CleartripProvider(
    api_key=os.getenv("CLEARTRIP_API_KEY", ""),
    api_secret=os.getenv("CLEARTRIP_API_SECRET", "")
)

emt_provider = EaseMyTripProvider(
    api_key=os.getenv("EMT_API_KEY", ""),
    api_secret=os.getenv("EMT_API_SECRET", "")
)

indigo_provider = IndigoProvider(
    api_key=os.getenv("INDIGO_API_KEY", ""),
    api_secret=os.getenv("INDIGO_API_SECRET", "")
)

riya_provider = RiyaTravelProvider(
    api_key=os.getenv("RIYA_API_KEY", ""),
    api_secret=os.getenv("RIYA_API_SECRET", "")
)

savaari_provider = SavaariProvider(
    api_key=os.getenv("SAVAARI_API_KEY", ""),
    api_secret=os.getenv("SAVAARI_API_SECRET", "")
)

# Create provider maps
travel_providers: Dict[str, TravelProvider] = {
    TravelProviderType.MMT.value: mmt_provider,
    TravelProviderType.CLEARTRIP.value: cleartrip_provider,
    TravelProviderType.EMT.value: emt_provider,
    TravelProviderType.INDIGO.value: indigo_provider,
    TravelProviderType.RIYA.value: riya_provider,
}

cab_providers: Dict[str, CabProvider] = {
    TravelProviderType.SAVAARI.value: savaari_provider,
}

# Create aggregator
aggregator = TravelAggregator(
    providers=travel_providers,
    cab_providers=cab_providers
)

@router.get("/flights/search", response_model=List[FlightResult])
async def search_flights(
    from_city: str,
    to_city: str,
    departure_date: datetime,
    return_date: Optional[datetime] = None,
    adults: int = Query(default=1, ge=1),
    children: int = Query(default=0, ge=0),
    class_type: str = "ECONOMY"
):
    """Search flights across all providers"""
    criteria = SearchCriteria(
        from_city=from_city,
        to_city=to_city,
        departure_date=departure_date,
        return_date=return_date,
        adults=adults,
        children=children,
        class_type=class_type
    )
    return await aggregator.search_all_flights(criteria)

@router.get("/hotels/search", response_model=List[HotelResult])
async def search_hotels(
    city: str,
    check_in: datetime,
    check_out: datetime,
    rooms: int = Query(default=1, ge=1),
    adults: int = Query(default=2, ge=1),
    children: int = Query(default=0, ge=0)
):
    """Search hotels across all providers"""
    criteria = HotelSearchCriteria(
        city=city,
        check_in=check_in,
        check_out=check_out,
        rooms=rooms,
        adults=adults,
        children=children
    )
    return await aggregator.search_all_hotels(criteria)

@router.get("/cabs/search", response_model=List[CabResult])
async def search_cabs(
    city: str,
    pickup_date: datetime,
    drop_date: Optional[datetime] = None,
    cab_type: str = "ALL"
):
    """Search cabs across all providers"""
    criteria = CabSearchCriteria(
        city=city,
        pickup_date=pickup_date,
        drop_date=drop_date,
        cab_type=cab_type
    )
    return await aggregator.search_all_cabs(criteria)

@router.get("/deals/best")
async def get_best_deals(
    from_city: str,
    to_city: str,
    departure_date: datetime,
    return_date: Optional[datetime] = None
):
    """Get best deals across all categories"""
    return await aggregator.get_best_deals(
        from_city=from_city,
        to_city=to_city,
        departure_date=departure_date,
        return_date=return_date
    )

@router.get("/prices/trends")
async def get_price_trends(from_city: str, to_city: str):
    """Get price trends from all providers"""
    return await aggregator.get_price_trends(from_city, to_city)
