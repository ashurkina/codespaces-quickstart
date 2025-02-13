from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from openai import OpenAI
from dotenv import load_dotenv
import os
import json
from pydantic import BaseModel

# Load environment variables
load_dotenv()

# Retrieve API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

# Define Pydantic model for button responses
class ButtonOption(BaseModel):
    title: str
    payload: str

class ButtonResponse(BaseModel):
    buttons: list[ButtonOption]

# Predefined suggestions example

SUGGESTIONS = [
    "Connect to human - I want to talk to a human agent",
    "Help - What can you do?"
]
message = "Here are some options:"

class ActionGenerateSuggestions(Action):

    model_name = 'gpt-4o-2024-08-06'

    def name(self) -> Text:
        return "action_generate_suggestions"

    def get_suggestion_list(self) -> List:
        return SUGGESTIONS
    
    def get_suggestion_message(self) -> str:
        return message
    
    def get_conversation_history(self, tracker: Tracker, num_turns: int = 5) -> str:
        """
        Retrieves the last `num_turns` user and bot messages as context.
        """
        history = []
        for event in tracker.events:
            if event.get("event") in ["user", "bot"] and "text" in event:
                role = "User" if event["event"] == "user" else "Bot"
                history.append(f"{role}: {event['text']}")
        
        return "\n".join(history[-num_turns:])  # Get last `num_turns` messages

    def generate_buttons(self, context: str) -> List[Dict[str, str]]:
        """
        Generates dynamic buttons based on the given context using OpenAI.
        """
        completion = client.beta.chat.completions.parse(
            model=self.model_name,
            messages=[
                {"role": "system", "content": f"""Generate two relevant button options for the given user query.
                                                     The button text should be 2-3 words, grammatically correct.
                                                     The payload should be 2-4 words, user-to-assistant style.
                                                     Choose from {self.get_suggestion_list()}.
                                                     Choose only relevant options. If nothing relevant choose two buttons from the list above."""},
                {"role": "user", "content": f"Context: {context}"},
            ],
            response_format=ButtonResponse,
        )
        
        button_data = completion.choices[0].message.parsed
        return [{"title": btn.title, "payload": btn.payload} for btn in button_data.buttons]

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Retrieve the last 5 turns of conversation history
        context = self.get_conversation_history(tracker, num_turns=5)

        # Generate contextual buttons
        buttons = self.generate_buttons(context)

        # Send response with buttons
        dispatcher.utter_message(text=self.get_suggestion_message(), buttons=buttons)
        
        return []
