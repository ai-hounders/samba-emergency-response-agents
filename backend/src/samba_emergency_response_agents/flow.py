from crewai.flow.flow import Flow, listen, start, router, or_, and_
from litellm import completion
from dotenv import load_dotenv
import os, asyncio
from typing import Dict
from samba_emergency_response_agents.emergency_monitoring_crew import EmergencyMonitoringCrew
from samba_emergency_response_agents.impact_analysis_crew import ImpactAnalysisCrew
from samba_emergency_response_agents.weather_monitoring_crew import WeatherMonitoringCrew
from samba_emergency_response_agents.high_risk_areas_search_crew import HighRiskAreasSearchCrew
from samba_emergency_response_agents.crew import SambaEmergencyResponseAgents
from samba_emergency_response_agents.image_analysis_crew import ImageAnalysisCrew
from pydantic import BaseModel

load_dotenv()

class EmergencyDatabase(BaseModel):
    event: dict = {}
    safe_places: list[dict] = []
    weather: dict = {}
    high_risk_areas: list[dict] = []
    image_analysis: str = ""
    event_analysis: str = ""
    high_risk_area_assessment_feedback: str = ""
    emergency_response: str = ""

class EmergencyResponseFlow(Flow[EmergencyDatabase]):
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

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
    def provide_emergency_remediation(self):
        print("****Starting Emergency Response Flow****")

        inputs = {
            "event_details": self.state.event
        }

        result = SambaEmergencyResponseAgents().crew().kickoff(inputs=inputs)

        # get raw output then save to state
        output = result.raw
        self.state.emergency_response = output
        print("Emergency Response JSON: \n", output)
        return output



async def main():
    flow = EmergencyResponseFlow()
    flow.plot("my_flow_plot")

    await flow.kickoff_async()

asyncio.run(main())