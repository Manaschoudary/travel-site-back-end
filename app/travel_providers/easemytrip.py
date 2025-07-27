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

class EaseMyTripProvider(TravelProvider):
    """EaseMyTrip API integration"""
    
    def __init__(self, api_key: str, api_secret: str, environment: str = "production"):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = "https://api.easemytrip.com/api/v1" if environment == "production" else "https://sandbox-api.easemytrip.com/api/v1"
        self.session = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "X-EMT-Key": api_key,
                "X-EMT-Secret": api_secret,
                "Content-Type": "application/json"
            }
        )
    
    async def search_flights(self, criteria: SearchCriteria) -> List[FlightResult]:
        """Search flights using EaseMyTrip API"""
        try:
            response = await self.session.post("/flights/search", json={
                "Origin": criteria.from_city,
                "Destination": criteria.to_city,
                "DepartureDate": criteria.departure_date.strftime("%Y-%m-%d"),
                "ReturnDate": criteria.return_date.strftime("%Y-%m-%d") if criteria.return_date else None,
                "AdultCount": criteria.adults,
                "ChildCount": criteria.children,
                "CabinClass": criteria.class_type,
                "PreferredAirlines": [],
                "Currency": "INR"
            })
            response.raise_for_status()
            data = response.json()

            return [
                FlightResult(
                    provider=TravelProviderType.EMT,
                    flight_number=flight["FlightNumber"],
                    airline=flight["AirlineName"],
                    departure_time=datetime.fromisoformat(flight["DepartureDateTime"]),
                    arrival_time=datetime.fromisoformat(flight["ArrivalDateTime"]),
                    price=float(flight["TotalFare"]),
                    available_seats=flight.get("AvailableSeats", 0),
                    class_type=criteria.class_type,
                    refundable=flight.get("IsRefundable", False),
                    deep_link=flight.get("DeepLink", ""),
                    provider_data=flight
                )
                for flight in data.get("Flights", [])
            ]
        except Exception as e:
            print(f"Error searching EMT flights: {str(e)}")
            return []

    async def search_hotels(self, criteria: HotelSearchCriteria) -> List[HotelResult]:
        """Search hotels using EaseMyTrip API"""
        try:
            response = await self.session.post("/hotels/search", json={
                "CityName": criteria.city,
                "CheckInDate": criteria.check_in.strftime("%Y-%m-%d"),
                "CheckOutDate": criteria.check_out.strftime("%Y-%m-%d"),
                "RoomCount": criteria.rooms,
                "AdultCount": criteria.adults,
                "ChildCount": criteria.children,
                "Currency": "INR"
            })
            response.raise_for_status()
            data = response.json()

            return [
                HotelResult(
                    provider=TravelProviderType.EMT,
                    hotel_name=hotel["HotelName"],
                    location=hotel["Location"],
                    check_in=criteria.check_in,
                    check_out=criteria.check_out,
                    price_per_night=float(hotel["PricePerNight"]),
                    total_price=float(hotel["TotalPrice"]),
                    room_type=hotel.get("RoomType", "Standard"),
                    amenities=hotel.get("Amenities", []),
                    rating=float(hotel.get("Rating", 0)),
                    deep_link=hotel.get("DeepLink", ""),
                    provider_data=hotel
                )
                for hotel in data.get("Hotels", [])
            ]
        except Exception as e:
            print(f"Error searching EMT hotels: {str(e)}")
            return []

    async def get_price_calendar(self, from_city: str, to_city: str) -> dict:
        """Get price calendar from EaseMyTrip"""
        try:
            response = await self.session.get(
                "/flights/fare-calendar",
                params={
                    "Origin": from_city,
                    "Destination": to_city,
                    "Currency": "INR"
                }
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error getting EMT price calendar: {str(e)}")
            return {}

    async def check_availability(self, booking_id: str) -> bool:
        """Check booking availability in EaseMyTrip"""
        try:
            response = await self.session.get(f"/booking/{booking_id}/status")
            response.raise_for_status()
            data = response.json()
            return data.get("IsAvailable", False)
        except Exception:
            return False
