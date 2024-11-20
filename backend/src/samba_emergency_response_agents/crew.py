import os

from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task

# Uncomment the following line to use an example of a custom tool
from samba_emergency_response_agents.tools.custom_tool import WildfireMonitorTool, GoogleRoutesTool, OpenWeatherMapTool, PlacesSearchTool

# Check our tools documentations for more information on how to use them
from crewai_tools import SerperDevTool, ScrapeWebsiteTool, DallETool

llama90b = LLM(
    model="sambanova/Llama-3.2-90B-Vision-Instruct",
    temperature=0.15,
    api_key=os.getenv("SAMBANOVA_API_KEY")
)

# llama90b_2 = LLM(
#     model="sambanova/Llama-3.2-90B-Vision-Instruct",
#     temperature=0.15,
#     api_key=os.getenv("SAMBANOVA_API_KEY_2")
# )

llama70b = LLM(
    model="sambanova/Meta-Llama-3.1-70B-Instruct",
    temperature=0.15,
    api_key=os.getenv("SAMBANOVA_API_KEY")
)

# llama70b_2 = LLM(
#     model="sambanova/Meta-Llama-3.1-70B-Instruct",
#     temperature=0.15,
#     api_key=os.getenv("SAMBANOVA_API_KEY_2")
# )

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
class SambaEmergencyResponseAgents():
    """SambaEmergencyResponseAgents crew"""

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    # @agent
    # def image_generator_agent(self) -> Agent:
    #     return Agent(
    #         config=self.agents_config['image_generator_agent'],
    #         tools=[DallETool()],
    #         verbose=True
    #     )

    @agent
    def evac_route_planning_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['evac_route_planning_agent'],
            tools=[GoogleRoutesTool()],
            verbose=True,
            llm=llama405b_2
        )

    @agent
    def monitoring_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['monitoring_agent'],
            tools=[WildfireMonitorTool()],
            verbose=True,
            llm=llama11b
        )

    @agent
    def weather_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['weather_agent'],
            tools=[OpenWeatherMapTool()],
            verbose=True,
            llm=llama70b
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
    def places_search_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['places_search_agent'],
            tools=[PlacesSearchTool()],
            verbose=True,
            llm=llama70b
        )

    @agent
    def impact_analysis_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['impact_analysis_agent'],
            verbose=True,
            llm=llama405b
        )

    @agent
    def resource_deployment_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['resource_deployment_agent'],
            verbose=True,
            tools=[PlacesSearchTool()],
            llm=llama70b
        )
    
    @agent
    def safe_zones_identifier_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['safe_zones_identifier_agent'],
            verbose=True,
            tools=[PlacesSearchTool()],
            llm=llama90b
        )

    @task
    def monitoring_task(self) -> Task:
        return Task(
            config=self.tasks_config['monitoring_task'],
            output_file="event.json"
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
    def weather_task(self) -> Task:
        return Task(
            config=self.tasks_config['weather_task'],
            context=[self.monitoring_task()],
            output_file="weather.json"
        )
    
    @task
    def places_search_task(self) -> Task:
        return Task(
            config=self.tasks_config['places_search_task'],
            context=[self.monitoring_task(), self.weather_task()],
            output_file="places.json"
        )
    
    @task
    def impact_analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config['impact_analysis_task'],
            context=[self.monitoring_task(), self.weather_task(), self.places_search_task()],
            output_file="impact_analysis.md",
            human_input=True
        )
    
    @task
    def resource_deployment_task(self) -> Task:
        return Task(
            config=self.tasks_config['resource_deployment_task'],
            context=[self.impact_analysis_task()],
            output_file="resource_deployment.md",
            human_input=True
        )
    
    @task
    def safe_zones_identifier_task(self) -> Task:
        return Task(
            config=self.tasks_config['safe_zones_identifier_task'],
            context=[self.impact_analysis_task(), self.resource_deployment_task()],
            output_file="safe_zones.md",
            human_input=True
        )

    ## For evacuation route planning
    @task
    def evac_route_planning_task(self) -> Task:
        return Task(
            config=self.tasks_config['evac_route_planning_task'],
            context=[self.impact_analysis_task(), self.resource_deployment_task(), self.safe_zones_identifier_task()],
            output_file="evac_routes.json"
        )

    @crew
    def crew(self) -> Crew:
        """Creates the SambaEmergencyResponseAgents crew"""
        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=False,
            # memory=True
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )
