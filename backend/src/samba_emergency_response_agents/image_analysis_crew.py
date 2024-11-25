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
class ImageAnalysisCrew():
    """Image Analysis Crew"""
    agents_config = "config/image_analysis_agents.yaml"
    tasks_config = "config/image_analysis_tasks.yaml"

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
