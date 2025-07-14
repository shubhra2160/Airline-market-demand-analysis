import httpx
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from ..config import settings

logger = logging.getLogger(__name__)

class AmadeusService:
    """Service for interacting with Amadeus API"""
    
    def __init__(self):
        self.base_url = settings.AMADEUS_BASE_URL
        self.api_key = settings.AMADEUS_API_KEY
        self.api_secret = settings.AMADEUS_API_SECRET
        self.access_token = None
        self.token_expires_at = None
        
    async def get_access_token(self) -> Optional[str]:
        """Get or refresh access token"""
        if self.access_token and self.token_expires_at and datetime.now() < self.token_expires_at:
            return self.access_token
            
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/v1/security/oauth2/token",
                    data={
                        "grant_type": "client_credentials",
                        "client_id": self.api_key,
                        "client_secret": self.api_secret
                    },
                    headers={"Content-Type": "application/x-www-form-urlencoded"}
                )
                
                if response.status_code == 200:
                    token_data = response.json()
                    self.access_token = token_data["access_token"]
                    # Token expires in seconds, we'll refresh 10 minutes early
                    expires_in = token_data.get("expires_in", 3600)
                    self.token_expires_at = datetime.now() + timedelta(seconds=expires_in - 600)
                    logger.info("Successfully obtained Amadeus access token")
                    return self.access_token
                else:
                    logger.error(f"Failed to get access token: {response.status_code} - {response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error getting access token: {str(e)}")
            return None
    
    async def search_flights(self, origin: str, destination: str, 
                           departure_date: str, return_date: str = None,
                           adults: int = 1, max_results: int = 100) -> Optional[List[Dict]]:
        """Search for flights between origin and destination"""
        token = await self.get_access_token()
        if not token:
            logger.error("No access token available")
            return None
            
        try:
            params = {
                "originLocationCode": origin,
                "destinationLocationCode": destination,
                "departureDate": departure_date,
                "adults": adults,
                "max": max_results
            }
            
            if return_date:
                params["returnDate"] = return_date
                
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/v2/shopping/flight-offers",
                    params=params,
                    headers={"Authorization": f"Bearer {token}"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    flights = data.get("data", [])
                    logger.info(f"Found {len(flights)} flights for {origin} -> {destination}")
                    return flights
                else:
                    logger.error(f"Flight search failed: {response.status_code} - {response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error searching flights: {str(e)}")
            return None
    
    async def get_flight_inspiration(self, origin: str, max_price: int = 1000) -> Optional[List[Dict]]:
        """Get flight inspiration/destinations from origin"""
        token = await self.get_access_token()
        if not token:
            return None
            
        try:
            params = {
                "origin": origin,
                "maxPrice": max_price
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/v1/shopping/flight-destinations",
                    params=params,
                    headers={"Authorization": f"Bearer {token}"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    destinations = data.get("data", [])
                    logger.info(f"Found {len(destinations)} destinations from {origin}")
                    return destinations
                else:
                    logger.error(f"Flight inspiration failed: {response.status_code} - {response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error getting flight inspiration: {str(e)}")
            return None
    
    async def get_flight_dates(self, origin: str, destination: str) -> Optional[List[Dict]]:
        """Get cheapest flight dates for a route"""
        token = await self.get_access_token()
        if not token:
            return None
            
        try:
            params = {
                "origin": origin,
                "destination": destination
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/v1/shopping/flight-dates",
                    params=params,
                    headers={"Authorization": f"Bearer {token}"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    dates = data.get("data", [])
                    logger.info(f"Found {len(dates)} date options for {origin} -> {destination}")
                    return dates
                else:
                    logger.error(f"Flight dates failed: {response.status_code} - {response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error getting flight dates: {str(e)}")
            return None
    
    async def get_airport_info(self, airport_code: str) -> Optional[Dict]:
        """Get airport information"""
        token = await self.get_access_token()
        if not token:
            return None
            
        try:
            params = {
                "keyword": airport_code,
                "subType": "AIRPORT"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/v1/reference-data/locations",
                    params=params,
                    headers={"Authorization": f"Bearer {token}"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    locations = data.get("data", [])
                    if locations:
                        return locations[0]
                    return None
                else:
                    logger.error(f"Airport info failed: {response.status_code} - {response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error getting airport info: {str(e)}")
            return None
    
    def parse_flight_data(self, flight_data: Dict) -> Dict:
        """Parse Amadeus flight data into our format"""
        try:
            # Extract basic flight information
            itinerary = flight_data.get("itineraries", [{}])[0]
            segment = itinerary.get("segments", [{}])[0]
            
            # Extract pricing
            price_info = flight_data.get("price", {})
            total_price = float(price_info.get("total", 0))
            currency = price_info.get("currency", "AUD")
            
            # Extract airline and flight details
            airline = segment.get("carrierCode", "")
            flight_number = segment.get("number", "")
            aircraft = segment.get("aircraft", {}).get("code", "")
            
            # Extract timing
            departure = segment.get("departure", {})
            arrival = segment.get("arrival", {})
            
            parsed_data = {
                "origin": departure.get("iataCode", ""),
                "destination": arrival.get("iataCode", ""),
                "departure_date": departure.get("at", ""),
                "arrival_date": arrival.get("at", ""),
                "airline": airline,
                "flight_number": flight_number,
                "aircraft_type": aircraft,
                "price": total_price,
                "currency": currency,
                "booking_class": segment.get("class", ""),
                "availability": flight_data.get("numberOfBookableSeats", 0),
                "duration": itinerary.get("duration", ""),
                "raw_data": flight_data
            }
            
            return parsed_data
            
        except Exception as e:
            logger.error(f"Error parsing flight data: {str(e)}")
            return {}
    
    async def get_domestic_flights(self, date_range: int = 7) -> List[Dict]:
        """Get domestic flights for Australian cities"""
        all_flights = []
        
        for origin in settings.AUSTRALIAN_CITIES:
            for destination in settings.AUSTRALIAN_CITIES:
                if origin != destination:
                    # Get flights for the next week
                    departure_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
                    
                    flights = await self.search_flights(
                        origin=origin,
                        destination=destination,
                        departure_date=departure_date,
                        max_results=20
                    )
                    
                    if flights:
                        for flight in flights:
                            parsed_flight = self.parse_flight_data(flight)
                            parsed_flight["is_domestic"] = True
                            all_flights.append(parsed_flight)
        
        return all_flights
    
    async def get_international_flights(self, date_range: int = 7) -> List[Dict]:
        """Get international flights from Australian cities"""
        all_flights = []
        
        for origin in settings.AUSTRALIAN_CITIES:
            for destination in settings.INTERNATIONAL_DESTINATIONS:
                departure_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
                
                flights = await self.search_flights(
                    origin=origin,
                    destination=destination,
                    departure_date=departure_date,
                    max_results=20
                )
                
                if flights:
                    for flight in flights:
                        parsed_flight = self.parse_flight_data(flight)
                        parsed_flight["is_domestic"] = False
                        all_flights.append(parsed_flight)
        
        return all_flights

# Create service instance
amadeus_service = AmadeusService() 