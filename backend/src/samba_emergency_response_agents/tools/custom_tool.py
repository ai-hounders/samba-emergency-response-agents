from crewai.tools import BaseTool
from typing import Type, Dict, List, Optional

from pydantic import BaseModel, Field 

import requests, json, os

from datetime import datetime, timedelta


# class MyCustomToolInput(BaseModel):
#     """Input schema for MyCustomTool."""
#     argument: str = Field(..., description="Description of the argument.")

# class MyCustomTool(BaseTool):
#     name: str = "Name of my tool"
#     description: str = (
#         "Clear description for what this tool is useful for, you agent will need this information to use it."
#     )
#     args_schema: Type[BaseModel] = MyCustomToolInput

#     def _run(self, argument: str) -> str:
#         # Implementation goes here
#         return "this is an example of a tool output, ignore it and move along."


class WildfireMonitorToolInput(BaseModel):
    """Input schema for WildfireMonitorTool."""
    days: int = Field(20, description="The number of days to consider for recent events.")
    status: str = Field("open", description="Status of the events to fetch (e.g., 'open').")


class WildfireMonitorTool(BaseTool):
    name: str = "Wildfire Monitoring Tool"
    description: str = (
        "A custom tool to monitor the latest wildfire events from NASA's EONET API. "
        "This tool fetches the most recent natural events related to wildfires and provides key details about them."
    )
    args_schema: Type[BaseModel] = WildfireMonitorToolInput

    def _run(self, days: int, status: str) -> str:
        try:
            # Constructing the API URL with the provided parameters
            url = f"https://eonet.gsfc.nasa.gov/api/v3/events?limit=5&days={days}&status={status}"
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            
            return json.dumps(data)
        except requests.exceptions.RequestException as e:
            return json.dumps({"error": f"Error while fetching wildfire events: {e}"})
        except Exception as e:
            return json.dumps({"error": f"Unexpected error: {e}"})


class GoogleRoutesToolInput(BaseModel):
    """Input schema for GoogleRoutesTool."""
    origin_latitude: float = Field(..., description="Latitude of the origin location.")
    origin_longitude: float = Field(..., description="Longitude of the origin location.")
    destination_latitude: float = Field(..., description="Latitude of the destination location.")
    destination_longitude: float = Field(..., description="Longitude of the destination location.")
    travel_mode: str = Field("DRIVE", description="Mode of travel. Can be DRIVE, BICYCLE, or WALK.")
    routing_preference: str = Field("TRAFFIC_AWARE", description="Routing preference. Can be TRAFFIC_AWARE, TRAFFIC_AWARE_OPTIMAL, or SHORTEST.")


class GoogleRoutesTool(BaseTool):
    name: str = "Google Routes Tool"
    description: str = (
        "A custom tool to fetch the route information from Google Routes API. "
        "This tool provides the optimal route, distance, and duration between an origin and a destination."
    )
    args_schema: Type[BaseModel] = GoogleRoutesToolInput

    def _run(self, origin_latitude: float, origin_longitude: float, destination_latitude: float, destination_longitude: float, travel_mode: str, routing_preference: str) -> dict:
        try:
            # Constructing the request payload
            payload = {
                "origin": {
                    "location": {
                        "latLng": {
                            "latitude": origin_latitude,
                            "longitude": origin_longitude
                        }
                    }
                },
                "destination": {
                    "location": {
                        "latLng": {
                            "latitude": destination_latitude,
                            "longitude": destination_longitude
                        }
                    }
                },
                "travelMode": travel_mode,
                "routingPreference": routing_preference,
                "computeAlternativeRoutes": False,
                "routeModifiers": {
                    "avoidTolls": False,
                    "avoidHighways": False,
                    "avoidFerries": False
                },
                "languageCode": "en-US",
                "units": "IMPERIAL"
            }

            # Sending the request to Google Routes API
            headers = {
                'Content-Type': 'application/json',
                'X-Goog-Api-Key': os.getenv('GOOGLE_MAPS_API_KEY'),
                'X-Goog-FieldMask': 'routes.duration,routes.distanceMeters,routes.polyline.encodedPolyline'
            }
            response = requests.post('https://routes.googleapis.com/directions/v2:computeRoutes', json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()

            # Extracting route information
            routes = data.get("routes", [])
            if not routes:
                return json.dumps({"error": "No routes found."})

            return routes
        except requests.exceptions.RequestException as e:
            return json.dumps({"error": f"Error while fetching route information: {e}"})
        except Exception as e:
            return json.dumps({"error": f"Unexpected error: {e}"})


class OpenWeatherMapToolInput(BaseModel):
    """Input schema for OpenWeatherTool."""
    latitude: float = Field(..., description="Latitude of the location for which weather information is required.")
    longitude: float = Field(..., description="Longitude of the location for which weather information is required.")
    count: int = Field(4, description="The number of 3-hourly intervals for which weather needs to be forecasted.")


class OpenWeatherMapTool(BaseTool):
    name: str = "Open Weather Map Tool"
    description: str = (
        "A custom tool to get the current, hourly, and alert weather data from OpenWeather API. "
        "It excludes minutely and daily weather information."
    )
    args_schema: Type[BaseModel] = OpenWeatherMapToolInput

    def _run(self, latitude: float, longitude: float, count: int) -> str:
        try:
            ## Ensuring to include high winds alert in the weather
            simulate_wind_alert = True;

            # Constructing the API URL
            api_key = os.getenv('OPENWEATHER_API_KEY')
            current_weather_url = f"https://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid={api_key}"

            forecast_weather_url = f"https://api.openweathermap.org/data/2.5/forecast?cnt={count}&lat={latitude}&lon={longitude}&appid={api_key}"

            # Making the API requests
            current_weather_response = requests.get(current_weather_url)
            forecast_weather_response = requests.get(forecast_weather_url)
            current_weather_response.raise_for_status()
            forecast_weather_response.raise_for_status()
            current = current_weather_response.json()
            forecast = forecast_weather_response.json()

            alerts = []

            # Simulate wind alert if requested
            if simulate_wind_alert:
                start_time = datetime.now() + timedelta(hours=2)
                end_time = start_time + timedelta(hours=1)
                alerts.append({
                    "sender_name": "Simulated Alert System",
                    "event": "High Winds Warning",
                    "start": start_time.isoformat() + "Z",
                    "end": end_time.isoformat() + "Z",
                    "description": "Strong winds expected with gusts up to 60 mph. Please take necessary precautions."
                })

            output = {
                "current": current,
                "forecast": forecast,
                "alerts": alerts
            }
            return json.dumps(output)
        except requests.exceptions.RequestException as e:
            return json.dumps({"error": f"Error while fetching weather information: {e}"})
        except Exception as e:
            return json.dumps({"error": f"Unexpected error: {e}"})


class PlacesSearchToolInput(BaseModel):
    """Input schema for PlacesSearchTool."""
    latitude: float = Field(..., description="Latitude of the center point for the places search.")
    longitude: float = Field(..., description="Longitude of the center point for the places search.")
    radius: int = Field(..., description="Radius in meters to search for places.")
    type: str = Field("locality", description="The type of places to search for. Default is 'locality' for cities and towns.")

class PlacesSearchTool(BaseTool):
    name: str = "Places Search Tool"
    description: str = (
        "A custom tool to fetch places within a specified radius using the Google Nearby Places API. "
    )
    args_schema: Type[BaseModel] = PlacesSearchToolInput

    def _run(self, latitude: float, longitude: float, radius: int, type: str) -> dict:
        try:
            # Constructing the API URL
            api_key = os.getenv('GOOGLE_MAPS_API_KEY')
            url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={latitude},{longitude}&radius={radius}&type={type}&key={api_key}"

            # Making the API request
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            # Extracting place information
            places = [
                {
                    "name": result.get("name"),
                    "location": result.get("geometry", {}).get("location", {})
                }
                for result in data.get("results", [])
            ]

            return {"places": places}
        except requests.exceptions.RequestException as e:
            return {"error": f"Error while fetching places information: {e}"}
        except Exception as e:
            return {"error": f"Unexpected error: {e}"}
