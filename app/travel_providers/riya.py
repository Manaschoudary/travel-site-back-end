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

class RiyaTravelProvider(TravelProvider):
    """Riya Travels API integration"""
    
    def __init__(self, api_key: str, api_secret: str, environment: str = "production"):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = "https://api.riya.travel/v1" if environment == "production" else "https://sandbox-api.riya.travel/v1"
        self.session = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Partner-ID": api_secret,
                "Content-Type": "application/json"
            }
        )
    
    async def search_flights(self, criteria: SearchCriteria) -> List[FlightResult]:
        """Search flights using Riya API"""
        try:
            response = await self.session.post("/flights/search", json={
                "source": criteria.from_city,
                "destination": criteria.to_city,
                "travelDate": criteria.departure_date.strftime("%Y-%m-%d"),
                "returnDate": criteria.return_date.strftime("%Y-%m-%d") if criteria.return_date else None,
                "adultPax": criteria.adults,
                "childPax": criteria.children,
                "cabinClass": criteria.class_type,
                "currency": "INR"
            })
            response.raise_for_status()
            data = response.json()

            return [
                FlightResult(
                    provider=TravelProviderType.RIYA,
                    flight_number=flight["flightNo"],
                    airline=flight["airlineName"],
                    departure_time=datetime.fromisoformat(flight["departureDateTime"]),
                    arrival_time=datetime.fromisoformat(flight["arrivalDateTime"]),
                    price=float(flight["totalFare"]),
                    available_seats=flight.get("seatsAvailable", 0),
                    class_type=criteria.class_type,
                    refundable=flight.get("refundable", False),
                    deep_link=flight.get("bookingLink", ""),
                    provider_data=flight
                )
                for flight in data.get("flightResults", [])
            ]
        except Exception as e:
            print(f"Error searching Riya flights: {str(e)}")
            return []

    async def search_hotels(self, criteria: HotelSearchCriteria) -> List[HotelResult]:
        """Search hotels using Riya API"""
        try:
            response = await self.session.post("/hotels/search", json={
                "city": criteria.city,
                "checkinDate": criteria.check_in.strftime("%Y-%m-%d"),
                "checkoutDate": criteria.check_out.strftime("%Y-%m-%d"),
                "noOfRooms": criteria.rooms,
                "adultCount": criteria.adults,
                "childCount": criteria.children,
                "currency": "INR"
            })
            response.raise_for_status()
            data = response.json()

            return [
                HotelResult(
                    provider=TravelProviderType.RIYA,
                    hotel_name=hotel["hotelName"],
                    location=hotel["location"],
                    check_in=criteria.check_in,
                    check_out=criteria.check_out,
                    price_per_night=float(hotel["pricePerNight"]),
                    total_price=float(hotel["totalPrice"]),
                    room_type=hotel.get("roomCategory", "Standard"),
                    amenities=hotel.get("amenities", []),
                    rating=float(hotel.get("starRating", 0)),
                    deep_link=hotel.get("bookingLink", ""),
                    provider_data=hotel
                )
                for hotel in data.get("hotelResults", [])
            ]
        except Exception as e:
            print(f"Error searching Riya hotels: {str(e)}")
            return []

    async def get_price_calendar(self, from_city: str, to_city: str) -> dict:
        """Get price calendar from Riya"""
        try:
            response = await self.session.get(
                "/flights/fare-calendar",
                params={
                    "source": from_city,
                    "destination": to_city,
                    "currency": "INR"
                }
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error getting Riya price calendar: {str(e)}")
            return {}

    async def check_availability(self, booking_id: str) -> bool:
        """Check booking availability in Riya"""
        try:
            response = await self.session.get(f"/bookings/{booking_id}/status")
            response.raise_for_status()
            data = response.json()
            return data.get("available", False)
        except Exception:
            return False
