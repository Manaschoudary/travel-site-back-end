from typing import List
import httpx
from datetime import datetime
from .base import TravelProvider
from .schemas import (
    SearchCriteria,
    HotelSearchCriteria,
    FlightResult,
    HotelResult,
    TravelProviderType
)

class MakeMyTripProvider(TravelProvider):
    def __init__(self, api_key: str, api_secret: str, environment: str = "production"):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = "https://api.makemytrip.com/api/v3" if environment == "production" else "https://sandbox-api.makemytrip.com/api/v3"
        self.session = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "X-API-Key": api_key,
                "X-API-Secret": api_secret,
                "Content-Type": "application/json"
            }
        )
    
    async def search_flights(self, criteria: SearchCriteria) -> List[FlightResult]:
        """Search for flights using MMT API"""
        try:
            response = await self.session.post("/flights/search", json={
                "fromCity": criteria.from_city,
                "toCity": criteria.to_city,
                "departureDate": criteria.departure_date.strftime("%Y-%m-%d"),
                "returnDate": criteria.return_date.strftime("%Y-%m-%d") if criteria.return_date else None,
                "adults": criteria.adults,
                "children": criteria.children,
                "classType": criteria.class_type
            })
            response.raise_for_status()
            data = response.json()
            
            return [
                FlightResult(
                    provider=TravelProviderType.MMT,
                    flight_number=flight["flightNumber"],
                    airline=flight["airlineName"],
                    departure_time=datetime.fromisoformat(flight["departureTime"]),
                    arrival_time=datetime.fromisoformat(flight["arrivalTime"]),
                    price=float(flight["fare"]["totalAmount"]),
                    available_seats=flight["availableSeats"],
                    class_type=flight["cabinClass"],
                    refundable=flight["isRefundable"],
                    deep_link=flight["deepLink"],
                    provider_data=flight
                )
                for flight in data["flights"]
            ]
        except Exception as e:
            print(f"Error searching MMT flights: {str(e)}")
            return []

    async def search_hotels(self, criteria: HotelSearchCriteria) -> List[HotelResult]:
        """Search for hotels using MMT API"""
        try:
            response = await self.session.post("/hotels/search", json={
                "city": criteria.city,
                "checkIn": criteria.check_in.strftime("%Y-%m-%d"),
                "checkOut": criteria.check_out.strftime("%Y-%m-%d"),
                "rooms": criteria.rooms,
                "adults": criteria.adults,
                "children": criteria.children
            })
            response.raise_for_status()
            data = response.json()
            
            return [
                HotelResult(
                    provider=TravelProviderType.MMT,
                    hotel_name=hotel["name"],
                    location=hotel["location"],
                    check_in=criteria.check_in,
                    check_out=criteria.check_out,
                    price_per_night=float(hotel["pricePerNight"]),
                    total_price=float(hotel["totalPrice"]),
                    room_type=hotel["roomType"],
                    amenities=hotel["amenities"],
                    rating=float(hotel["rating"]),
                    deep_link=hotel["deepLink"],
                    provider_data=hotel
                )
                for hotel in data["hotels"]
            ]
        except Exception as e:
            print(f"Error searching MMT hotels: {str(e)}")
            return []

    async def get_price_calendar(self, from_city: str, to_city: str) -> dict:
        """Get price calendar for flexible dates"""
        try:
            response = await self.session.get(
                "/flights/calendar",
                params={
                    "fromCity": from_city,
                    "toCity": to_city,
                    "months": 3  # Get prices for next 3 months
                }
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error getting MMT price calendar: {str(e)}")
            return {}

    async def check_availability(self, booking_id: str) -> bool:
        """Check if a particular booking ID is still available"""
        try:
            response = await self.session.get(f"/booking/{booking_id}/availability")
            response.raise_for_status()
            data = response.json()
            return data["available"]
        except Exception:
            return False
