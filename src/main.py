"""
By Aarish Kodnaney
"""

from dataclasses import dataclass
from langchain.tools import tool, ToolRuntime
from dotenv import load_dotenv
from weather import Weather, WeatherInfo
import os

from langchain.chat_models import init_chat_model
from langgraph.checkpoint.memory import InMemorySaver
from langchain.agents.structured_output import ToolStrategy
from langchain.agents import create_agent

load_dotenv()
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
checkpointer = InMemorySaver()

SYSTEM_PROMPT = """
You are an expert weather forecaster, who does not speak in puns or joke around whatsoever.
You tell the weather to the user, and then tell them one thing they should watch out for.
Examples of things to watch out for could be sunburn, frostbite, avalanches, etc. 

You have access to three tools:
- get_weather_for_location: use this to get weather for a specific location.
- get_user_location: use this to get the user's location
- raise_issue: use this if you aren't sure what to do. It's most likely use case will be if
you cannot find a user's location.

If a user asks you for the weather, make sure you are aware of the location. If, from the
question, you can tell where they are, use the get_user_location tool to find their location.
If you cannot tell where they are, use raise_issue.
"""

# creating tools
@tool
def get_weather_for_location(city: str) -> str:
    "Get weather for a given city"
    weather = Weather(WEATHER_API_KEY, "http://api.weatherapi.com/v1")
    data = weather.get_data_from_endpoint(city)
    desired_info = weather.get_desired_info(data)
    official_info: WeatherInfo = weather.build_weather_info_obect(desired_info)
    return f"In {official_info.location}, the temperature is {official_info.temp_fahrenheit} degrees fahrenheit with weather conditions: {official_info.text_description}. Wind speed is {official_info.wind_speed_mph} mph"

@dataclass
class Context:
    user_id: str

@dataclass
class ResponseFormat:
    """Response schema for agent"""
    # weather information including temp, wind speed, text description, and location
    weather_info: str | None = None

    # what to watch our for
    watch_our_for: str| None = None



@tool
def get_user_location(runtime: ToolRuntime[Context]) -> str:
    """Retrieve user info based on user id."""
    user_id = runtime.context.user_id
    return "Boston" if user_id == "1" else "San Francisco"

model = init_chat_model(
    "claude-sonnet-4-5-20250929",
    temperature = 0.5,
    timeout=10,
    max_tokens=1000
)


agent = create_agent(
    model=model,
    system_prompt=SYSTEM_PROMPT,
    tools=[get_weather_for_location, get_user_location],
    context_schema=Context,
    response_format=ToolStrategy(ResponseFormat),
    checkpointer=checkpointer
)

config = {
    "configurable": {
        "thread_id": "1"
    }
}

response = agent.invoke(
    {
        "messages": [{
                "role": "user",
                "content": "what is the weather outside"
            }]
    },
    config = config,
    context=Context(user_id="ye")
)

print(response['structured_response'])