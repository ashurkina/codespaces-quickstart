from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import ConversationPaused

class ActionHandoffToHuman(Action):
    def name(self) -> Text:
        return "action_handoff_to_human"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:
        
        dispatcher.utter_message(text="Transferring you to a human agent. Please wait...")
        
        # Logic to connect to human agent (e.g., API call, CRM integration)
        dispatcher.utter_message(text="A human agent has been notified and will join shortly.")
        
        return [ConversationPaused()]