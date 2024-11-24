import os, base64

from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task

from samba_emergency_response_agents.tools.custom_tool import WildfireMonitorTool, GoogleRoutesTool, OpenWeatherMapTool, PlacesSearchTool

from crewai_tools import SerperDevTool, ScrapeWebsiteTool, DallETool

llama90b = LLM(
    model="sambanova/Llama-3.2-90B-Vision-Instruct",
    temperature=0.15,
    api_key=os.getenv("SAMBANOVA_API_KEY")
)

llama90b_2 = LLM(
    model="sambanova/Llama-3.2-90B-Vision-Instruct",
    temperature=0.15,
    api_key=os.getenv("SAMBANOVA_API_KEY_2")
)

llama70b = LLM(
    model="sambanova/Meta-Llama-3.1-70B-Instruct",
    temperature=0.15,
    api_key=os.getenv("SAMBANOVA_API_KEY")
)

llama70b_2 = LLM(
    model="sambanova/Meta-Llama-3.1-70B-Instruct",
    temperature=0.15,
    api_key=os.getenv("SAMBANOVA_API_KEY_2")
)

llama405b = LLM(
    model="sambanova/Meta-Llama-3.1-405B-Instruct",
    temperature=0.15,
    api_key=os.getenv("SAMBANOVA_API_KEY")
)

llama405b_2 = LLM(
    model="sambanova/Meta-Llama-3.1-405B-Instruct",
    temperature=0.15,
    api_key=os.getenv("SAMBANOVA_API_KEY_2")
)

llama8b = LLM(
    model="sambanova/Meta-Llama-3.1-8B-Instruct",
    temperature=0.15,
    api_key=os.getenv("SAMBANOVA_API_KEY")
)

llama11b = LLM(
    model="sambanova/Llama-3.2-11B-Vision-Instruct",
    temperature=0.15,
    api_key=os.getenv("SAMBANOVA_API_KEY")
)

@CrewBase
class EmergencyMonitoringCrew():
    """Emergency Monitoring Crew"""
    @agent
    def monitoring_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['monitoring_agent'],
            tools=[WildfireMonitorTool()],
            verbose=True,
            llm=llama8b
        )
    
    @task
    def monitoring_task(self) -> Task:
        return Task(
            config=self.tasks_config['monitoring_task'],
            output_file="event.json"
        )
    
    @crew
    def crew(self) -> Crew:
        """Creates the Emergency Monitoring Crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks, 
            process=Process.sequential,
            memory=True
        )

@CrewBase
class WeatherMonitoringCrew():
    """Weather Monitoring Crew"""
    @agent
    def weather_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['weather_agent'],
            tools=[OpenWeatherMapTool()],
            verbose=True,
            llm=llama11b
        )

    @task
    def weather_task(self) -> Task:
        return Task(
            config=self.tasks_config['weather_task'],
            output_file="weather.json"
        )
    
    @crew
    def crew(self) -> Crew:
        """Creates the Weather Monitoring Crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks, 
            process=Process.sequential,
            memory=True
        )
    
@CrewBase
class HighRiskAreasAssessmentCrew():
    """High Risk Areas Assessment Crew"""
    @agent
    def high_risk_places_search_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['high_risk_places_search_agent'],
            tools=[PlacesSearchTool()],
            verbose=True,
            llm=llama90b
        )
    
    @task
    def high_risk_places_search_task(self) -> Task:
        return Task(
            config=self.tasks_config['high_risk_places_search_task'],
            output_file="high_risk_places.json"
        )

    @crew
    def crew(self) -> Crew:
        """Creates the High Risk Areas Assessment Crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks, 
            process=Process.sequential,
            memory=True,
            planning=True #May require multiple calls to the tool to calculate the radius and locate the high risk areas.
        )

@CrewBase
class ImageAnalysisCrew():
    """Image Analysis Crew"""
    @agent
    def image_analysis_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['image_analysis_agent'],
            verbose=True,
            llm=llama90b_2
        )
    
    @task
    def image_analysis_task(self) -> Task:
        image_path = "./src/samba_emergency_response_agents/images/satellite/wildfire_2.jpg"
        with open(image_path, "rb") as image_file:
            image_data = image_file.read()

        encoded_image = base64.b64encode(image_data).decode('utf-8')
        
        output_path = "image_analysis.md"
        print("hello im here")
        return Task(
            config=self.tasks_config['image_analysis_task'],
            input_file=encoded_image,
            output_file=output_path
        )
    
    @crew
    def crew(self) -> Crew:
        """Creates the Image Analysis Crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks, 
            process=Process.sequential,
            memory=True
        )
    

@CrewBase
class ImpactAnalysisCrew():
    """Impact Analysis Crew"""
    @agent
    def impact_analysis_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['impact_analysis_agent'],
            verbose=True,
            llm=llama405b
        )
    
    @task
    def impact_analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config['impact_analysis_task'],
            output_file="event_impact_analysis.md"
        )
    
    @crew
    def crew(self) -> Crew:
        """Creates the Impact Analysis Crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks, 
            process=Process.sequential,
            memory=True
        )

@CrewBase
class SambaEmergencyResponseAgents():
    """SambaEmergencyResponseAgents crew"""




    # @agent
    # def image_generator_agent(self) -> Agent:
    #     return Agent(
    #         config=self.agents_config['image_generator_agent'],
    #         tools=[DallETool()],
    #         verbose=True
    #     )

    
    
    @agent
    def route_planning_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['route_planning_agent'],
            tools=[GoogleRoutesTool()],
            verbose=True,
            llm=llama405b_2
        )

    

    # @agent
    # def communication_agent(self) -> Agent:
    #     return Agent(
    #         config=self.agents_config['communication_agent'],
    #         verbose=True,
    #         tools=[SerperDevTool(), ScrapeWebsiteTool()],
    #         llm=llama70b
    #     )

    

  

    @agent
    def resource_deployment_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['resource_deployment_agent'],
            verbose=True,
            tools=[PlacesSearchTool()],
            llm=llama70b_2
        )
    
    @agent
    def safe_zones_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['safe_zones_agent'],
            verbose=True,
            tools=[PlacesSearchTool()],
            llm=llama90b
        )

   
    

   

    # @task
    # def communication_task(self) -> Task:
    #     return Task(
    #         config=self.tasks_config['communication_task'],
    #         context=[self.evacuation_task(), self.resource_task()],
    #         output_file='public_announcement.md'
    #     )

    # @task
    # def image_generation_task(self) -> Task:
    #     return Task(
    #         config=self.tasks_config['image_generation_task'],
    #         context=[self.monitoring_task()]
    #     )
    
    
    
    
    
    @task
    def resource_deployment_task(self) -> Task:
        return Task(
            config=self.tasks_config['resource_deployment_task'],
            output_file="resource_deployment.md",
        )
    
    @task
    def safe_zones_task(self) -> Task:
        return Task(
            config=self.tasks_config['safe_zones_task'],
            output_file="safe_zones.json",
        )

    ## For evacuation route planning
    @task
    def route_planning_task(self) -> Task:
        return Task(
            config=self.tasks_config['route_planning_task'],
            context=[self.impact_analysis_task(), self.high_risk_places_search_task(), self.safe_zones_task()],
            output_file="evac_routes.json"
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Emergency Monitoring Crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks, 
            process=Process.sequential,
            verbose=False,
            memory=True,
            # planning=True,
            # planning_llm=llama405b_2
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )
