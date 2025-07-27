import httpx
from typing import List
from datetime import datetime
from app.travel_providers.base import TravelProvider
from app.travel_providers.schemas import (
    SearchCriteria,
    HotelSearchCriteria,
    FlightResult,
    HotelResult,
    TravelProviderType
)

class IndigoProvider(TravelProvider):
    """Indigo Airlines API integration"""
    
    def __init__(self, api_key: str, api_secret: str, environment: str = "production"):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = "https://api.goindigo.in/api/v1" if environment == "production" else "https://sandbox-api.goindigo.in/api/v1"
        self.session = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "X-API-Key": api_key,
                "X-API-Secret": api_secret,
                "Content-Type": "application/json"
            }
        )
    
    async def search_flights(self, criteria: SearchCriteria) -> List[FlightResult]:
        """Search Indigo flights"""
        try:
            response = await self.session.post("/availability/search", json={
                "origin": criteria.from_city,
                "destination": criteria.to_city,
                "date": criteria.departure_date.strftime("%Y-%m-%d"),
                "returnDate": criteria.return_date.strftime("%Y-%m-%d") if criteria.return_date else None,
                "adults": criteria.adults,
                "children": criteria.children,
                "infantCount": 0,
                "cabinClass": criteria.class_type,
                "currencyCode": "INR"
            })
            response.raise_for_status()
            data = response.json()

            return [
                FlightResult(
                    provider=TravelProviderType.INDIGO,
                    flight_number=flight["flightNumber"],
                    airline="Indigo",
                    departure_time=datetime.fromisoformat(flight["departureTime"]),
                    arrival_time=datetime.fromisoformat(flight["arrivalTime"]),
                    price=float(flight["fareDetails"]["totalFare"]),
                    available_seats=flight.get("availableSeats", 0),
                    class_type=criteria.class_type,
                    refundable=flight.get("isRefundable", False),
                    deep_link=flight.get("bookingLink", ""),
                    provider_data=flight
                )
                for flight in data.get("flights", [])
            ]
        except Exception as e:
            print(f"Error searching Indigo flights: {str(e)}")
            return []

    async def search_hotels(self, criteria: HotelSearchCriteria) -> List[HotelResult]:
        """Indigo doesn't provide hotel bookings"""
        return []

    async def get_price_calendar(self, from_city: str, to_city: str) -> dict:
        """Get Indigo price calendar"""
        try:
            response = await self.session.get(
                "/fare-calendar",
                params={
                    "origin": from_city,
                    "destination": to_city,
                    "currency": "INR"
                }
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error getting Indigo price calendar: {str(e)}")
            return {}

    async def check_availability(self, booking_id: str) -> bool:
        """Check Indigo booking availability"""
        try:
            response = await self.session.get(f"/bookings/{booking_id}")
            response.raise_for_status()
            data = response.json()
            return data.get("status") == "CONFIRMED"
        except Exception:
            return False
