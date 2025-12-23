"""
By Aarish Kodnaney
"""

import dotenv
import json
from typing import Any
from langchain.agents import create_agent

dotenv.load_dotenv()


def get_weather(city: str) -> str:
    """
    Get weather for a given city
    """
    return f"It's always dreaful in {city}"

agent: Any = create_agent(
    model="claude-sonnet-4-20250514",
    tools=[get_weather],
    system_prompt="you are a helpful assistant"
)

# running the agent
result = agent.invoke(
    {"messages": [
            {
                "role": "user",
                "content": "what is the weather in sf"
            }
        ]
    }
)

with open("agent_output.txt", "w") as f:
    for message in result["messages"]:
        f.write(f"{message.type}: {message.content}\n\n")
        print(f"{message.type}: {message.content}\n\n")
