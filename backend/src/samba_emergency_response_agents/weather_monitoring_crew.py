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
class WeatherMonitoringCrew():
    """Weather Monitoring Crew"""
    agents_config = "config/weather_agents.yaml"
    tasks_config = "config/weather_tasks.yaml"

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
 