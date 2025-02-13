from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

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
   
    #Calls the external API to check visa requirements.
   
    headers = {"Authorization": f"Bearer {VISA_API_KEY}"}
    params = {"passport": passport, "destination": destination}
    
    response = requests.post(VISA_API_URL, headers=headers, params=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"API request failed: {response.status_code}, {response.text}"}


def openai_visa_check(passport: str, destination: str, message: str) -> str:
  
    #Uses OpenAI to process a visa check query.
   
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

class ActionCheckVisaRequirements(Action):
    def name(self) -> Text:
        return "action_check_visa_requirements"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Extracting entities (passport country and destination)
        passport = tracker.get_slot("passport")
        destination = tracker.get_slot("destination")

        if not passport or not destination:
            dispatcher.utter_message(text="I need both passport country and destination to check visa requirements.")
            return []

        # Extract the last three user messages from tracker
        user_messages = [
            event["text"] for event in tracker.events 
            if event.get("event") == "user" and "text" in event][-3:]  # Get the last three messages

        context = "\n".join(user_messages) if user_messages else "No previous messages available."

        # Construct the message with conversation context
        message = f"""
                    You need to answer the user's question. 
                    Don't share any links to any resources or add any non-related information. 
                    Just answer the question. The user is traveling to {destination} with a {passport} passport. 
                    Here is the context of the conversation:\n\n {context}"""

        # Call OpenAI function
        visa_info = openai_visa_check(passport, destination, message)

        dispatcher.utter_message(text=f"{visa_info}")

        return []   