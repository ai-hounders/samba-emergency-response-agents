import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import streamlit as st
import json
# Load wildfire incident data
with open("../backend/event.json", "r") as f:
    event_data = json.load(f)

# Extract wildfire coordinates
incident_coords = event_data["geometry"][0]["coordinates"]
incident_df = pd.DataFrame([{
    "name": event_data["title"],
    "lat": incident_coords[1],  # latitude
    "lon": incident_coords[0]   # longitude
}])


# Load data from JSON files
input_file = "../backend/places.json"

# Read the file with single quotes and fix it
with open(input_file, "r") as f:
    content = f.read()

# Replace single quotes with double quotes
content = content.replace("'", '"')

places_data = json.loads(content)  # Ensure the structure is valid JSON


places_df = pd.DataFrame([{
    "name": place["name"],
    "lon": place["location"]["lat"],
    "lat": place["location"]["lng"]
} for place in places_data["places"]])

wildfire_icon = {
    "url": "https://img.icons8.com/ios-filled/50/FF0000/fire-element.png",  # Fire icon URL
    "width": 128,
    "height": 128,
    "anchorY": 128,
}

safe_zone_icon = {
    "url": "https://img.icons8.com/ios-filled/50/008000/home.png",  # Safe zone icon URL
    "width": 128,
    "height": 128,
    "anchorY": 128,
}


incident_df["icon_data"] = [wildfire_icon] * len(incident_df)
places_df["icon_data"] = [safe_zone_icon] * len(places_df)


# with open("../backend/evac_routes.json", "r") as f:
#     evac_data = json.load(f)

# Display map with wildfire and impacted areas
st.title("Wildfire Incident and Impacted Areas Map")

# Wildfire Layer
wildfire_layer = pdk.Layer(
    "IconLayer",
    data=incident_df,
    get_position="[lon, lat]",
    get_icon="icon_data",
    get_size=4,
    size_scale=10,
    pickable=True,
)

# Safe Zone Layer
safe_zone_layer = pdk.Layer(
    "IconLayer",
    data=places_df,
    get_position="[lon, lat]",
    get_icon="icon_data",
    get_size=4,
    size_scale=10,
    pickable=True,
)

st.pydeck_chart(
    pdk.Deck(
        map_style="mapbox://styles/mapbox/light-v9",
        initial_view_state=pdk.ViewState(
            latitude=incident_coords[1],  # Latitude of the wildfire
            longitude=incident_coords[0],  # Longitude of the wildfire
            zoom=8,
            pitch=45,
        ),
        layers=[
            # Wildfire incident point in red
            pdk.Layer(
                "ScatterplotLayer",
                data=incident_df,
                get_position="[lon, lat]",
                get_color="[255, 0, 0, 160]",  # Red color for wildfire
                get_radius=10000,
                pickable=True,
            ),
            # Impacted areas in orange
            pdk.Layer(
                "ScatterplotLayer",
                data=places_df,
                get_position="[lon, lat]",
                get_color="[255, 165, 0, 160]",  # Orange for impacted areas
                get_radius=500,
                pickable=True,
            ),
            wildfire_layer, safe_zone_layer
        ],
    )
)

st.write("Wildfire Incident Data")
st.write(incident_df)

st.write("Impacted Areas Data")
st.write(places_df)