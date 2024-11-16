from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field


from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field

import requests


# class MyCustomToolInput(BaseModel):
#     """Input schema for MyCustomTool."""
#     argument: str = Field(..., description="Description of the argument.")

# class MyCustomTool(BaseTool):
#     name: str = "Name of my tool"
#     description: str = (
#         "Clear description for what this tool is useful for, you agent will need this information to use it."
#     )
#     args_schema: Type[BaseModel] = MyCustomToolInput

#     def _run(self, argument: str) -> str:
#         # Implementation goes here
#         return "this is an example of a tool output, ignore it and move along."



class WildfireMonitorToolInput(BaseModel):
    """Input schema for WildfireMonitorTool."""
    limit: int = Field(5, description="The number of events to fetch.")
    days: int = Field(20, description="The number of days to consider for recent events.")
    status: str = Field("open", description="Status of the events to fetch (e.g., 'open').")


class WildfireMonitorTool(BaseTool):
    name: str = "Wildfire Monitoring Tool"
    description: str = (
        "A custom tool to monitor the latest wildfire events from NASA's EONET API. "
        "This tool fetches the most recent natural events related to wildfires and provides key details about them."
    )
    args_schema: Type[BaseModel] = WildfireMonitorToolInput

    def _run(self, limit: int, days: int, status: str) -> str:
        try:
            # Constructing the API URL with the provided parameters
            url = f"https://eonet.gsfc.nasa.gov/api/v3/events?limit={limit}&days={days}&status={status}"
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            events = data.get("events", [])

            # Formatting the output for the latest wildfire events
            output = "Latest Wildfire Events:\n"
            for event in events:
                event_title = event.get("title", "No title")
                event_link = event.get("link", "No link")
                event_date = event["geometry"][0].get("date", "No date")
                output += f"- {event_title} (Date: {event_date})\n  More info: {event_link}\n"

            return output
        except requests.exceptions.RequestException as e:
            return f"Error while fetching wildfire events: {e}"
        except Exception as e:
            return f"Unexpected error: {e}"

