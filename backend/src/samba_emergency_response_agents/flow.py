from crewai.flow.flow import Flow, listen, start, router, or_, and_
from litellm import completion
from dotenv import load_dotenv
import os, asyncio
from typing import Dict
from samba_emergency_response_agents.crew import EmergencyMonitoringCrew, HighRiskAreasSearchCrew, WeatherMonitoringCrew, ImpactAnalysisCrew, SafeZonesCrew, ResourceDeploymentCrew, RoutePlanningCrew, ImageAnalysisCrew
from pydantic import BaseModel
from samba_emergency_response_agents.types import HighRiskAreas, SafeZones, Routes

load_dotenv()

class EmergencyDatabase(BaseModel):
    event: dict = {}
    safe_zones: SafeZones = None
    weather: dict = {}
    high_risk_areas: HighRiskAreas = None
    image_analysis: str = ""
    event_analysis: str = ""
    high_risk_area_assessment_feedback: str = ""
    emergency_response: str = ""
    evacuation_routes: Routes = None
    resource_deployment: str = ""

"""
EmergencyResponseFlow handles the orchestration of emergency response activities.

This flow coordinates multiple crews and agents to:
1. Monitor emergency events (wildfires) using EONET data
2. Track weather conditions that could affect the emergency
3. Identify high-risk areas within potential spread radius
4. Analyze impact and provide response recommendations

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
        inputs = {
        }

        result = EmergencyMonitoringCrew().crew().kickoff(inputs=inputs)

        # get raw output then save to state
        output = result.raw
        self.state.event = output
        print("Event Info JSON: \n", output)
        return output

    """
    Listen for emergency events and monitor weather conditions that could affect the emergency.
    """
    @listen(monitor_emergency_events)
    def monitor_weather(self):
        print("****Starting Weather Monitoring Flow****")

        inputs = {
            "event_details": self.state.event,
        }

        result = WeatherMonitoringCrew().crew().kickoff(inputs=inputs)

        # get raw output then save to state
        output = result.raw
        self.state.weather = output
        print("Weather JSON: \n", output)
        return output
    
    """
    Listen for weather data and emergency events. Assess high-risk areas within potential spread radius.
    Also, listen for feedback from the impact assessment step to further refine high-risk area assessment.
    """
    @listen(or_(and_(monitor_weather, monitor_emergency_events), "high_risk_area_assessment_feedback"))
    def assess_high_risk_areas(self):
        print("****Starting High Risk Areas Assessment Flow****")

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
        output = result.raw
        self.state.high_risk_areas = output
        print("High Risk Areas JSON: \n", output)
        return output

    """
    Listen for emergency events. Analyze images to provide additional context and insights.
    """
    @listen(monitor_emergency_events)
    def analyze_images(self):
        print("****Starting Image Analysis Flow****")

        inputs = {
            "event_details": self.state.event
        }

        result = ImageAnalysisCrew().crew().kickoff(inputs=inputs)

        # get raw output then save to state
        output = result.raw
        self.state.image_analysis = output
        print("Image Analysis JSON: \n", output)
        return output

    """
    Listen for emergency events, weather data, high-risk areas, and image analysis.
    Assess the impact of the emergency and provide recommendations for response actions.
    """
    @listen(and_(monitor_emergency_events, monitor_weather, assess_high_risk_areas, analyze_images))
    def assess_impact(self):
        print("****Starting Impact Assessment Flow****")

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
        print("Event Analysis JSON: \n", output)
        return output
    
    """
    Provide feedback on the impact assessment. This feedback can be used to refine the high-risk area assessment.
    """
    @router(assess_impact)
    def provide_impact_assessment_feedback(self):
        print(f"Review the wildfire emergency and its impact.")

        # Present options to the user
        print("\nPlease choose an option:")
        print("1. False emergency.")
        print("2. Redo high risk areas assessment with additional feedback.")
        print("3. Proceed with emergency response.")

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

    @listen("proceed_to_emergency_remediation")
    def determine_safe_zones(self):
        print("****Starting Safe Zone Determination Flow****")

        inputs = {
            "event_analysis": self.state.event_analysis
        }

        result = SafeZonesCrew().crew().kickoff(inputs=inputs)

        # get raw output then save to state
        output = result.raw
        self.state.safe_zones = output
        print("Safe Zones JSON: \n", output)
        return output


    @listen("proceed_to_emergency_remediation")
    def deploy_resources(self):
        print("****Starting Resource Deployment Flow****")

        inputs = {
            "event_analysis": self.state.event_analysis
        }

        result = ResourceDeploymentCrew().crew().kickoff(inputs=inputs)

        # get raw output then save to state
        output = result.raw
        self.state.resource_deployment = output
        print("Resource Deployment JSON: \n", output)
        return output
    
    @listen(and_(determine_safe_zones))
    def plan_evacuation_routes(self):
        print("****Starting Evacuation Route Planning Flow****")

        inputs = {
            "event_analysis": self.state.event_analysis,
            "high_risk_areas": self.state.high_risk_areas,
            "safe_zones": self.state.safe_zones
        }

        result = RoutePlanningCrew().crew().kickoff(inputs=inputs)

        # get raw output then save to state
        output = result.raw
        self.state.evacuation_routes = output
        print("Evacuation Routes JSON: \n", output)
        return output



async def main():
    flow = EmergencyResponseFlow()
    flow.plot("my_flow_plot")

    await flow.kickoff_async()

asyncio.run(main())