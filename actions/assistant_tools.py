import os
import json
import requests
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve API keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
VISA_API_KEY = os.getenv("VISA_API_KEY")

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

VISA_API_URL = "https://zylalabs.com/api/5364/global+visa+check+api/6944/visa+check"


def check_visa_requirements(passport: str, destination: str) -> dict:
    """
    Calls the external API to check visa requirements.
    """
    headers = {"Authorization": f"Bearer {VISA_API_KEY}"}
    params = {"passport": passport, "destination": destination}
    
    response = requests.post(VISA_API_URL, headers=headers, params=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"API request failed: {response.status_code}, {response.text}"}


def openai_visa_check(passport: str, destination: str, message: str) -> str:
    """
    Uses OpenAI to process a visa check query.
    """
    tools = [{
        "type": "function",
        "function": {
            "name": "check_visa_requirements",
            "description": "Check visa requirements for a specified passport and destination.",
            "parameters": {
                "type": "object",
                "properties": {
                    "passport": {"type": "string", "description": "Country code of the passport."},
                    "destination": {"type": "string", "description": "Country code of the destination."}
                },
                "required": ["passport", "destination"],
                "additionalProperties": False
            },
            "strict": True
        }
    }]

    messages = [{"role": "user", "content": message}]

    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        tools=tools
    )

    tool_call = completion.choices[0].message.tool_calls[0]
    args = json.loads(tool_call.function.arguments)

    # Call the actual visa check function
    result = check_visa_requirements(args["passport"], args["destination"])

    messages.append(completion.choices[0].message)  # append model's function call message
    messages.append({                               # append result message
    "role": "tool",
    "tool_call_id": tool_call.id,
    "content": str(result)
    })

    completion_2 = client.chat.completions.create(
    model="gpt-4o",
    messages=messages,
    tools=tools,
    )

    return completion_2.choices[0].message.content
