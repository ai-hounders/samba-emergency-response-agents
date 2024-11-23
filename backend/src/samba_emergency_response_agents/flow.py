from crewai.flow.flow import Flow, listen, start, or_, and_
from litellm import completion
from dotenv import load_dotenv
import os, asyncio, dict
from crew import SambaEmergencyResponseAgents
from pydantic import BaseModel

load_dotenv()

class EmergencyDatabase(BaseModel):
    event: dict = {}
    safe_places: list[dict] = []
    weather: dict = {}
    high_risk_areas: list[dict] = []
    image_analysis: str = ""
    event_analysis: str = ""

class EmergencyResponseFlow(Flow[EmergencyDatabase]):

    @start()
    def impact_assessment(self):
        print("****Starting Impact Assessment Flow****")

        inputs = {
        }

        result = SambaEmergencyResponseAgents().crew().kickoff(inputs=inputs)

        # get raw output then save to state
        output = result.raw
        self.state.event_analysis = output

        return output

    @listen(impact_assessment)
    def emergency_response(self, event_analysis):
        print("****Starting Emergency Response Flow****")
        output = "hello"
        print(output)

        return event_analysis

    # @listen(generate_news)
    # def save_news(self, news):
    #     print("Saving news")
        
    #     # Create the news directory if it doesn't exist
    #     news_dir = os.path.join(os.path.dirname(__file__), "..", "..", "news")
    #     os.makedirs(news_dir, exist_ok=True)
        
    #     # Save the news in the news directory
    #     news_file_path = os.path.join(news_dir, "news.md")
    #     with open(news_file_path, "w") as f:
    #         f.write(news)
        
    #     print(f"News saved to: {news_file_path}")

    # @listen(generate_news)
    # def generate_best_news(self, input):
    #     print("Generating best news")
        
    #     response = completion(
    #         model=self.model,
    #         messages=[
    #             {
    #                 "role": "user",
    #                 "content": f"Choose the most important news from the following and return it: {input}",
    #             },
    #         ],
    #     )

    #     important_news = response["choices"][0]["message"]["content"]
    #     return important_news
    
    # @listen(and_(generate_news_topic, generate_news, save_news, generate_best_news))
    # def logger(self, result):
    #     print(f"Logger: {result}")
    #     print("*" * 100)
    #     print("News Complete!")


async def main():
    flow = EmergencyResponseFlow()
    flow.plot("my_flow_plot")

    await flow.kickoff()

asyncio.run(main())