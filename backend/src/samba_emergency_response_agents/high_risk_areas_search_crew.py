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
class HighRiskAreasSearchCrew():
    """High Risk Areas Assessment Crew"""
    agents_config = "config/high_risk_places_search_agents.yaml"
    tasks_config = "config/high_risk_places_search_tasks.yaml"

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
            memory=True
        )
