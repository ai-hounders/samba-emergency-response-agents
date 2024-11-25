import os
import json
from dotenv import load_dotenv
import streamlit as st

# Load environment variables
load_dotenv()
API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

# Load wildfire evacuation routes data
with open("evac_routes.json", "r") as f:
    evac_routes = json.load(f)

# Load safe zones data
with open("safe_zones.json", "r") as f:
    safe_zones = json.load(f)

# Load event data
with open("event.json", "r") as f:
    event_data = json.load(f)

# Load high-risk places data
with open("high_risk_places.json", "r") as f:
    high_risk_areas = json.load(f)

# Extract route information
routes_js_array = [
    {"origin": route["origin"], "destination": route["destination"]}
    for route in evac_routes["routes"]
]

# Extract safe zones
safe_zones_js_array = []
for category, locations in safe_zones.items():
    for location in locations:
        safe_zones_js_array.append({
            "name": location["name"],
            "lat": location["location"]["lat"],
            "lng": location["location"]["lng"],
            "category": category
        })

# Extract event geometry for the marker
event_marker = {
    "title": event_data["title"],
    "lat": event_data["geometry"][0]["coordinates"][1],  # Latitude
    "lng": event_data["geometry"][0]["coordinates"][0],  # Longitude
}

# Extract high-risk places
high_risk_js_array = [
    {"name": place["name"], "lat": place["location"]["lat"], "lng": place["location"]["lng"]}
    for place in high_risk_areas["high_risk_areas"]
]

# HTML Template with Dynamic Data
html_template = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Evacuation Routes, Safe Zones, and High-Risk Areas</title>
    <script src="https://maps.googleapis.com/maps/api/js?key={API_KEY}"></script>
    <script>
        function initMap() {{
            // Center map on event location
            const eventLatLng = {{ lat: {event_marker['lat']}, lng: {event_marker['lng']} }};
            const map = new google.maps.Map(document.getElementById("map"), {{
                zoom: 12,
                center: eventLatLng
            }});

            // Add routes
            const routes = {json.dumps(routes_js_array)};
            routes.forEach((route, index) => {{
                const directionsService = new google.maps.DirectionsService();
                const directionsRenderer = new google.maps.DirectionsRenderer({{
                    map: map,
                    polylineOptions: {{
                        strokeColor: index === 0 ? "red" : "blue",
                    }},
                }});

                directionsService.route(
                    {{
                        origin: route.origin,
                        destination: route.destination,
                        travelMode: google.maps.TravelMode.DRIVING,
                    }},
                    (result, status) => {{
                        if (status === "OK") {{
                            directionsRenderer.setDirections(result);
                        }} else {{
                            console.error("Error fetching directions: " + status);
                        }}
                    }}
                );
            }});

            // Add safe zones as markers
            const safeZones = {json.dumps(safe_zones_js_array)};
            safeZones.forEach((zone) => {{
                new google.maps.Marker({{
                    position: {{ lat: zone.lat, lng: zone.lng }},
                    map: map,
                    title: `${{zone.name}} (${{zone.category}})`,
                    icon: {{
                        path: google.maps.SymbolPath.CIRCLE,
                        scale: 10,
                        fillColor: "green",
                        fillOpacity: 0.8,
                        strokeWeight: 1,
                        strokeColor: "white"
                    }},
                }});
            }});

            // Add high-risk areas as markers
            const highRiskAreas = {json.dumps(high_risk_js_array)};
            highRiskAreas.forEach((area) => {{
                new google.maps.Marker({{
                    position: {{ lat: area.lat, lng: area.lng }},
                    map: map,
                    title: area.name,
                    icon: {{
                        path: google.maps.SymbolPath.CIRCLE,
                        scale: 10,
                        fillColor: "orange",
                        fillOpacity: 0.9,
                        strokeWeight: 1,
                        strokeColor: "white"
                    }},
                }});
            }});

            // Add event marker
            const eventMarker = {json.dumps(event_marker)};
            new google.maps.Marker({{
                position: {{ lat: eventMarker.lat, lng: eventMarker.lng }},
                map: map,
                title: eventMarker.title,
                icon: {{
                    path: google.maps.SymbolPath.BACKWARD_CLOSED_ARROW,
                    scale: 20,
                    fillColor: "red",
                    fillOpacity: 0.9,
                    strokeWeight: 2,
                    strokeColor: "white"
                }},
            }});
        }}
    </script>
</head>
<body onload="initMap()">
    <h1>Evacuation Routes, Safe Zones, and High-Risk Areas</h1>
    <div id="map" style="height: 600px; width: 100%;"></div>
</body>
</html>
"""

# Render the HTML in Streamlit
st.title("Evacuation Routes, Safe Zones, and High-Risk Areas")
st.write("Below are the evacuation routes, safe zones, high-risk areas, and event locations displayed on the same map.")
st.components.v1.html(html_template, height=700)


image_path = "../backend/src/samba_emergency_response_agents/images/satellite/wildfire_2.jpg"
analysis_path = "../backend/image_analysis.md"

st.header("Image Analysis")
st.image(image_path, caption="Satellite Image: Wildfire Area", use_container_width=True)

# Use a scrollable text area for the analysis at the bottom

with open(analysis_path, "r") as f:
        analysis_content = f.read()
st.markdown(
    f"""
    <div style="height: 400px; overflow-y: scroll; padding: 10px; border: 1px solid #ddd; border-radius: 5px;">
        {analysis_content}
    </div>
    """,
    unsafe_allow_html=True,
)


impact_analysis_path = "../backend/event_impact_analysis.md"

st.header("Event Impact Analysis")

with open(impact_analysis_path, "r") as f:
        impact_analysis_content = f.read()
st.markdown(
    f"""
    <div style="height: 600px; overflow-y: scroll; padding: 10px; border: 1px solid #ddd; border-radius: 5px;">
        {impact_analysis_content}
    </div>
    """,
    unsafe_allow_html=True,
)

