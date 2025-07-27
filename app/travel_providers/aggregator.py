from typing import List, Dict
from datetime import datetime
from .base import TravelProvider, CabProvider
from .schemas import (
    SearchCriteria,
    HotelSearchCriteria,
    CabSearchCriteria,
    FlightResult,
    HotelResult,
    CabResult
)

class TravelAggregator:
    """Aggregates results from multiple travel providers"""
    
    def __init__(self, providers: Dict[str, TravelProvider], cab_providers: Dict[str, CabProvider]):
        self.providers = providers
        self.cab_providers = cab_providers
    
    async def search_all_flights(self, criteria: SearchCriteria) -> List[FlightResult]:
        """Search flights across all providers"""
        all_results = []
        for provider in self.providers.values():
            results = await provider.search_flights(criteria)
            all_results.extend(results)
        
        # Sort by price
        return sorted(all_results, key=lambda x: x.price)
    
    async def search_all_hotels(self, criteria: HotelSearchCriteria) -> List[HotelResult]:
        """Search hotels across all providers"""
        all_results = []
        for provider in self.providers.values():
            results = await provider.search_hotels(criteria)
            all_results.extend(results)
        
        # Sort by total price
        return sorted(all_results, key=lambda x: x.total_price)
    
    async def search_all_cabs(self, criteria: CabSearchCriteria) -> List[CabResult]:
        """Search cabs across all providers"""
        all_results = []
        for provider in self.cab_providers.values():
            results = await provider.search_cabs(criteria)
            all_results.extend(results)
        
        # Sort by total price
        return sorted(all_results, key=lambda x: x.total_price)
    
    async def get_best_deals(
        self,
        from_city: str,
        to_city: str,
        departure_date: datetime,
        return_date: datetime | None = None
    ) -> Dict[str, List]:
        """Get best deals across all categories"""
        flight_criteria = SearchCriteria(
            from_city=from_city,
            to_city=to_city,
            departure_date=departure_date,
            return_date=return_date
        )
        
        hotel_criteria = HotelSearchCriteria(
            city=to_city,
            check_in=departure_date,
            check_out=return_date or departure_date
        )
        
        cab_criteria = CabSearchCriteria(
            city=to_city,
            pickup_date=departure_date,
            drop_date=return_date
        )
        
        # Get results from all providers
        flights = await self.search_all_flights(flight_criteria)
        hotels = await self.search_all_hotels(hotel_criteria)
        cabs = await self.search_all_cabs(cab_criteria)
        
        return {
            "flights": flights[:5],  # Top 5 flight deals
            "hotels": hotels[:5],    # Top 5 hotel deals
            "cabs": cabs[:5]         # Top 5 cab deals
        }
    
    async def get_price_trends(self, from_city: str, to_city: str) -> Dict[str, dict]:
        """Get price trends from all providers"""
        trends = {}
        for name, provider in self.providers.items():
            calendar = await provider.get_price_calendar(from_city, to_city)
            trends[name] = calendar
        return trends
