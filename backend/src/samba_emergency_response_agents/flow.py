from crewai.flow.flow import Flow, listen, start, router, or_, and_
from litellm import completion
from dotenv import load_dotenv
import streamlit as st
import os, asyncio, json
from typing import Dict
from string import Template
from samba_emergency_response_agents.crew import EmergencyMonitoringCrew, HighRiskAreasSearchCrew, WeatherMonitoringCrew, ImpactAnalysisCrew, SafeZonesCrew, ResourceDeploymentCrew, RoutePlanningCrew, ImageAnalysisCrew
from pydantic import BaseModel
from samba_emergency_response_agents.types import HighRiskAreas, SafeZones, Routes

load_dotenv()
API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
st.title("🌩️ Emergency Response Platform")

if "messages" not in st.session_state:
    st.session_state["messages"] = []

# Display existing messages
for msg in st.session_state["messages"]:
    st.chat_message(msg["role"]).write(msg["content"])

class EmergencyDatabase(BaseModel):
    event: dict = {}
    event_marker: dict = {}
    safe_zones: SafeZones = None
    weather: dict = {}
    high_risk_areas: HighRiskAreas = None
    image_analysis: str = ""
    event_analysis: str = ""
    high_risk_area_assessment_feedback: str = ""
    emergency_response: str = ""
    evacuation_routes: Routes = None
    resource_deployment: str = ""
    spread_radius: int = 0

"""
EmergencyResponseFlow handles the orchestration of emergency response activities.

This flow coordinates multiple crews and agents to:
1. Monitor emergency events (wildfires) using EONET data
2. Track weather conditions that could affect the emergency
3. Identify high-risk areas within potential spread radius
4. Analyze impact
5. Determine safe zones
6. Plan evacuation routes
7. Deploy resources

The flow maintains state using EmergencyDatabase to share data between steps.
Each step builds on previous results to create a comprehensive emergency response.
"""
class EmergencyResponseFlow(Flow[EmergencyDatabase]):
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    """
    Start the flow by monitoring emergency events. This step fetches wildfire events from EONET data.
    """
    @start()
    def monitor_emergency_events(self):
        print("**** Starting Emergency Monitoring ****")
        st.chat_message("assistant").write("Starting Emergency Monitoring...")
        inputs = {
        }
        
        result = EmergencyMonitoringCrew().crew().kickoff(inputs=inputs)

        # get raw output then save to state
        output = json.loads(result.raw)
        self.state.event = output
        st.chat_message("assistant").write(f"Event Info JSON: \n \n {output}")
        
        # Extract event geometry for the marker
        event_marker = {
            "title": output["title"],
            "lat": output["geometry"][0]["coordinates"][1],  # Latitude
            "lng": output["geometry"][0]["coordinates"][0],  # Longitude
        }
        self.state.event_marker = event_marker
        html = html_template_event.substitute(event_marker=json.dumps(event_marker), API_KEY=API_KEY)
        st.components.v1.html(html, height=700)
        # print("Event Info JSON: \n", output)
        return output

    """
    Listen for emergency events and monitor weather conditions that could affect the emergency.
    """
    @listen(monitor_emergency_events)
    def monitor_weather(self):
        print("****Starting Weather Monitoring Flow****")
        st.chat_message("assistant").write("Starting Weather Monitoring Flow...")
        inputs = {
            "event_details": self.state.event,
        }

        result = WeatherMonitoringCrew().crew().kickoff(inputs=inputs)

        # get raw output then save to state
        output = result.raw
        self.state.weather = output
        st.chat_message("assistant").write(f"Weather JSON:\n\n{output}")
        # print("Weather JSON: \n", output)
        return output
    
    """
    Listen for weather data and emergency events. Assess high-risk areas within potential spread radius.
    Also, listen for feedback from the impact assessment step to further refine high-risk area assessment.
    """
    @listen(or_(monitor_weather, "high_risk_area_assessment_feedback"))
    def assess_high_risk_areas(self):
        print("****Starting High Risk Areas Assessment Flow****")
        st.chat_message("assistant").write("Starting High Risk Areas Assessment Flow...")
        # Check if required data is in state
        if not self.state.weather:
            print("Warning: Weather data not available in state")
            exit()
            
        if not self.state.event:
            print("Warning: Event data not available in state") 
            exit()

        inputs = {
            "event_details": self.state.event,
            "weather_information": self.state.weather,
            "high_risk_area_assessment_feedback": self.state.high_risk_area_assessment_feedback
        }

        result = HighRiskAreasSearchCrew().crew().kickoff(inputs=inputs)

        # get raw output then save to state
        output = json.loads(result.raw)
        st.chat_message("assistant").write(f"High Risk Areas JSON:\n\n{output}")
        self.state.spread_radius = output["spread_radius"]
        # Extract high-risk places
        high_risk_areas= [
            {"name": place["name"], "lat": place["location"]["lat"], "lng": place["location"]["lng"]}
            for place in output["high_risk_areas"]
        ]
        self.state.high_risk_areas = high_risk_areas
        html = html_template_high_risk_areas.substitute(event_marker=json.dumps(self.state.event_marker), high_risk_areas=json.dumps(high_risk_areas), API_KEY=API_KEY)
        
        st.components.v1.html(html, height=700)
        # print("High Risk Areas JSON: \n", output)
        return output

    """
    Listen for emergency events. Analyze images to provide additional context and insights.
    """
    @listen(monitor_emergency_events)
    def analyze_images(self):
        print("****Starting Image Analysis Flow****")
        st.chat_message("assistant").write("Starting Image Analysis Flow...")
        inputs = {
            "event_details": self.state.event
        }

        result = ImageAnalysisCrew().crew().kickoff(inputs=inputs)

        # get raw output then save to state
        output = result.raw
        self.state.image_analysis = output

        image_path = "../backend/src/samba_emergency_response_agents/images/satellite/wildfire_2.jpg"

        st.header("Image Analysis")
        st.image(image_path, caption="Satellite Image: Wildfire Area", use_container_width=True)
        st.chat_message("assistant").write(f"Image Analysis:\n\n{output}")

        # print("Image Analysis: \n", output)
        return output

    """
    Listen for emergency events, weather data, high-risk areas, and image analysis.
    Assess the impact of the emergency and provide recommendations for response actions.
    """
    @listen(and_(monitor_emergency_events, monitor_weather, assess_high_risk_areas, analyze_images))
    def assess_impact(self):
        print("****Starting Impact Assessment Flow****")
        st.chat_message("assistant").write("Starting Impact Assessment Flow...")
        inputs = {
            "event_details": self.state.event,
            "weather_information": self.state.weather,
            "high_risk_areas": self.state.high_risk_areas,
            "image_analysis": self.state.image_analysis
        }

        result = ImpactAnalysisCrew().crew().kickoff(inputs=inputs)

        # get raw output then save to state
        output = result.raw
        self.state.event_analysis = output
        st.chat_message("assistant").write(f"Event Analysis: {output}")
        # print("Event Analysis: \n", output)
        return output
    
    """
    Provide feedback on the impact assessment. This feedback can be used to refine the high-risk area assessment.
    """
    @router(assess_impact)
    def provide_impact_assessment_feedback(self):
        print(f"Review the wildfire emergency and its impact.")
        st.chat_message("assistant").write("Review the wildfire emergency and its impact.")
        # Present options to the user
        print("\nPlease choose an option:")
        print("1. False emergency.")
        print("2. Redo high risk areas assessment with additional feedback.")
        print("3. Proceed with emergency response.")

        st.chat_message("assistant").write("Please choose an option from the console:\n1. False emergency.\n2. Redo high risk areas assessment with additional feedback.\n3. Proceed with emergency response.")

        choice = input("Enter the number of your choice: ")
        if choice == "1":
            print("Exiting the program.")
            exit()
        elif choice == "2":
            feedback = input(
                "\nPlease provide additional feedback on high risk area assessment:\n"
            )
            self.state.weather_feedback = feedback
            print("\nRe-running high risk area assessment with your feedback....")
            return "high_risk_area_assessment_feedback"
        elif choice == "3":
            print("\nProceeding to emergency response.")
            return "proceed_to_emergency_remediation"
        else:
            print("\nInvalid choice. Please try again.")
            return "impact_assessment_feedback"

    #    # Add a submit button to confirm selection
    #     if st.button("Submit Decision"):
    #         print(f"choice, {choice}")
    #         if choice == "1. False emergency.":
    #             st.chat_message("assistant").write("Exiting the program.")
    #             print("Exiting the program.")
    #             exit()
    #         elif choice == "2. Redo high risk areas assessment with additional feedback.":
    #             # Add a text input for feedback
    #             feedback = st.text_input("Please provide additional feedback on high risk area assessment:")
    #             if feedback:  # Only proceed if feedback is provided
    #                 self.state.high_risk_area_assessment_feedback = feedback
    #                 st.chat_message("assistant").write(f"Re-running high risk area assessment with your feedback....")
    #                 print(f"Re-running high risk area assessment with your feedback....")
    #                 return "high_risk_area_assessment_feedback"
    #         elif choice == "3. Proceed with emergency response.":
    #             st.chat_message("assistant").write("Proceeding to emergency response.")
    #             print("\nProceeding to emergency response.")
    #             return "proceed_to_emergency_remediation"
    #         else:
    #             st.chat_message("assistant").write("Invalid choice. Please try again.")
    #             print("\nInvalid choice. Please try again.")
    #             return "impact_assessment_feedback"

    #     # Return None if no button press yet
    #     # return "proceed_to_emergency_remediation"
    
    @listen("proceed_to_emergency_remediation")
    def determine_safe_zones(self):
        print("****Starting Safe Zone Determination Flow****")
        st.chat_message("assistant").write("Starting Safe Zone Determination Flow...")
        inputs = {
            "event_details": self.state.event,
            "high_risk_areas": self.state.high_risk_areas,
            "spread_radius": self.state.spread_radius
        }

        result = SafeZonesCrew().crew().kickoff(inputs=inputs)

        # get raw output then save to state
        output = json.loads(result.raw)
        
        st.chat_message("assistant").write(f"Safe Zones JSON: \n{output}")

        # Extract safe zones
        safe_zones = [
            {"name": place["name"], "lat": place["location"]["lat"], "lng": place["location"]["lng"]}
            for place in output["safe_zones"]
        ]
        self.state.safe_zones = safe_zones

        html = html_template_safe_areas.substitute(event_marker=json.dumps(self.state.event_marker), safe_zones=json.dumps(safe_zones), API_KEY=API_KEY, high_risk_areas=json.dumps(self.state.high_risk_areas))
        
        st.components.v1.html(html, height=700)
        # print("Safe Zones JSON: \n", output)
        return output


    @listen("proceed_to_emergency_remediation")
    def deploy_resources(self):
        print("****Starting Resource Deployment Flow****")
        st.chat_message("assistant").write("Starting Resource Deployment Flow...")
        inputs = {
            "event_analysis": self.state.event_analysis
        }

        result = ResourceDeploymentCrew().crew().kickoff(inputs=inputs)

        # get raw output then save to state
        output = result.raw
        self.state.resource_deployment = output
        st.chat_message("assistant").write(f"Resource Deployment: \n \n{output}")
        # print("Resource Deployment JSON: \n", output)
        return output
    
    @listen(determine_safe_zones)
    def plan_evacuation_routes(self):
        print("****Starting Evacuation Route Planning Flow****")
        st.chat_message("assistant").write("Starting Evacuation Route Planning Flow...")
        inputs = {
            "event_details": self.state.event,
            "high_risk_areas": self.state.high_risk_areas,
            "safe_zones": self.state.safe_zones
        }

        result = RoutePlanningCrew().crew().kickoff(inputs=inputs)

        # get raw output then save to state
        output = json.loads(result.raw)
        self.state.evacuation_routes = output
        st.chat_message("assistant").write(f"Evacuation Routes JSON: {output}")

        #Extract route information
        routes = [
            {"origin": route["route"]["origin"], "destination": route["route"]["destination"]}
            for route in output["routes"]
        ]

        st.header("Evacuation Routes, Safe Zones, and High-Risk Areas")
        st.write("Below are the evacuation routes, safe zones, high-risk areas, and event locations displayed on the same map.")
        html = html_template_routes.substitute(event_marker=json.dumps(self.state.event_marker), safe_zones=json.dumps(self.state.safe_zones), API_KEY=API_KEY, high_risk_areas=json.dumps(self.state.high_risk_areas), routes=json.dumps(routes))
        
        st.components.v1.html(html, height=700)
        # print("Evacuation Routes JSON: \n", output)
        return output



async def main():
    flow = EmergencyResponseFlow()
    flow.plot("my_flow_plot")

    # Start flow execution
    st.chat_message("assistant").write("Initializing emergency response flow...")

    await flow.kickoff_async()

html_template_event = Template("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Evacuation Routes, Safe Zones, and High-Risk Areas</title>
        <script src="https://maps.googleapis.com/maps/api/js?key=${API_KEY}"></script>
        <script>
            function initMap() {
            
                // Center map on event location
                const event_marker = ${event_marker};
                const eventLatLng = {lat: event_marker.lat, lng: event_marker.lng };
                const map = new google.maps.Map(document.getElementById("map"), {
                    zoom: 9,
                    center: eventLatLng
                });

                // Add event marker
                new google.maps.Marker({
                    position: eventLatLng,
                    map: map,
                    title: event_marker.title,
                    icon: {
                        path: google.maps.SymbolPath.BACKWARD_CLOSED_ARROW,
                        scale: 20,
                        fillColor: "red",
                        fillOpacity: 0.9,
                        strokeWeight: 2,
                        strokeColor: "white"
                    },
                });
            
                               
            }
        </script>
    </head>
    <body onload="initMap()">
        <div id="map" style="height: 600px; width: 100%;"></div>
    </body>
    </html>
    """)

html_template_high_risk_areas = Template("""
    <!DOCTYPE html>
        <html>
        <head>
            <title>Evacuation Routes, Safe Zones, and High-Risk Areas</title>
            <script src="https://maps.googleapis.com/maps/api/js?key=${API_KEY}"></script>
            <script>
                function initMap() {
                
                    // Center map on event location
                    const event_marker = ${event_marker};
                    const eventLatLng = {lat: event_marker.lat, lng: event_marker.lng };
                    const map = new google.maps.Map(document.getElementById("map"), {
                        zoom: 9,
                        center: eventLatLng
                    });

                    // Add event marker
                    new google.maps.Marker({
                        position: eventLatLng,
                        map: map,
                        title: event_marker.title,
                        icon: {
                            path: google.maps.SymbolPath.BACKWARD_CLOSED_ARROW,
                            scale: 20,
                            fillColor: "red",
                            fillOpacity: 0.9,
                            strokeWeight: 2,
                            strokeColor: "white"
                        },
                    });
                                         
                    // Add high-risk areas as markers
                    const highRiskAreas = ${high_risk_areas};
                    highRiskAreas.forEach((area) => {
                        new google.maps.Marker({
                            position: { lat: area.lat, lng: area.lng },
                            map: map,
                            title: area.name,
                            icon: {
                                path: google.maps.SymbolPath.CIRCLE,
                                scale: 10,
                                fillColor: "orange",
                                fillOpacity: 0.9,
                                strokeWeight: 1,
                                strokeColor: "white"
                            },
                        });
                    });
                
                                
                }
            </script>
        </head>
        <body onload="initMap()">
            <div id="map" style="height: 600px; width: 100%;"></div>
        </body>
        </html>
        """)


html_template_safe_areas = Template("""
    <!DOCTYPE html>
        <html>
        <head>
            <title>Evacuation Routes, Safe Zones, and High-Risk Areas</title>
            <script src="https://maps.googleapis.com/maps/api/js?key=${API_KEY}"></script>
            <script>
                function initMap() {
                
                    // Center map on event location
                    const event_marker = ${event_marker};
                    const eventLatLng = {lat: event_marker.lat, lng: event_marker.lng };
                    const map = new google.maps.Map(document.getElementById("map"), {
                        zoom: 9,
                        center: eventLatLng
                    });

                    // Add event marker
                    new google.maps.Marker({
                        position: eventLatLng,
                        map: map,
                        title: event_marker.title,
                        icon: {
                            path: google.maps.SymbolPath.BACKWARD_CLOSED_ARROW,
                            scale: 20,
                            fillColor: "red",
                            fillOpacity: 0.9,
                            strokeWeight: 2,
                            strokeColor: "white"
                        },
                    });
                                         
                    // Add high-risk areas as markers
                    const highRiskAreas = ${high_risk_areas};
                    highRiskAreas.forEach((area) => {
                        new google.maps.Marker({
                            position: { lat: area.lat, lng: area.lng },
                            map: map,
                            title: area.name,
                            icon: {
                                path: google.maps.SymbolPath.CIRCLE,
                                scale: 10,
                                fillColor: "orange",
                                fillOpacity: 0.9,
                                strokeWeight: 1,
                                strokeColor: "white"
                            },
                        });
                    });
                
                     // Add safe zones as markers
                    const safeZones = ${safe_zones};
                    safeZones.forEach((zone) => {
                        new google.maps.Marker({
                            position: { lat: zone.lat, lng: zone.lng },
                            map: map,
                            title: zone.name + " ("+zone.type+")",
                            icon: {
                                path: google.maps.SymbolPath.CIRCLE,
                                scale: 10,
                                fillColor: "green",
                                fillOpacity: 0.8,
                                strokeWeight: 1,
                                strokeColor: "white"
                            },
                        });
                    });
                                
                }
            </script>
        </head>
        <body onload="initMap()">
            <div id="map" style="height: 600px; width: 100%;"></div>
        </body>
        </html>
        """)

html_template_routes = Template("""
    <!DOCTYPE html>
        <html>
        <head>
            <title>Evacuation Routes, Safe Zones, and High-Risk Areas</title>
            <script src="https://maps.googleapis.com/maps/api/js?key=${API_KEY}"></script>
            <script>
                function initMap() {
                
                    // Center map on event location
                    const event_marker = ${event_marker};
                    const eventLatLng = {lat: event_marker.lat, lng: event_marker.lng };
                    const map = new google.maps.Map(document.getElementById("map"), {
                        zoom: 9,
                        center: eventLatLng
                    });

                    // Add event marker
                    new google.maps.Marker({
                        position: eventLatLng,
                        map: map,
                        title: event_marker.title,
                        icon: {
                            path: google.maps.SymbolPath.BACKWARD_CLOSED_ARROW,
                            scale: 20,
                            fillColor: "red",
                            fillOpacity: 0.9,
                            strokeWeight: 2,
                            strokeColor: "white"
                        },
                    });
                                         
                    // Add high-risk areas as markers
                    const highRiskAreas = ${high_risk_areas};
                    highRiskAreas.forEach((area) => {
                        new google.maps.Marker({
                            position: { lat: area.lat, lng: area.lng },
                            map: map,
                            title: area.name,
                            icon: {
                                path: google.maps.SymbolPath.CIRCLE,
                                scale: 10,
                                fillColor: "orange",
                                fillOpacity: 0.9,
                                strokeWeight: 1,
                                strokeColor: "white"
                            },
                        });
                    });
                
                     // Add safe zones as markers
                    const safeZones = ${safe_zones};
                    safeZones.forEach((zone) => {
                        new google.maps.Marker({
                            position: { lat: zone.lat, lng: zone.lng },
                            map: map,
                            title: zone.name + " ("+zone.type+")",
                            icon: {
                                path: google.maps.SymbolPath.CIRCLE,
                                scale: 10,
                                fillColor: "green",
                                fillOpacity: 0.8,
                                strokeWeight: 1,
                                strokeColor: "white"
                            },
                        });
                    });
                                
                    
                    // Add routes
                    const routes = ${routes};
                    routes.forEach((route, index) => {
                        const directionsService = new google.maps.DirectionsService();
                        const directionsRenderer = new google.maps.DirectionsRenderer({
                            map: map,
                            polylineOptions: {
                                strokeColor: "blue",
                                suppressMarkers: true
                            },
                        });

                        directionsService.route({
                                origin: route.origin,
                                destination: route.destination,
                                travelMode: google.maps.TravelMode.DRIVING,
                            },
                            (result, status) => {
                                if (status === "OK") {
                                    directionsRenderer.setDirections(result);
                                } else {
                                    console.error(`Route ${index + 1} failed: ` + status);
                                }
                            }
                        );
                    });
                                
                }
            </script>
        </head>
        <body onload="initMap()">
            <div id="map" style="height: 600px; width: 100%;"></div>
        </body>
        </html>
        """)
                                         
asyncio.run(main())

