from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from rasa_sdk.events import ConversationPaused
from actions.assistant_tools import openai_visa_check


class ActionSearchFlights(Action):
    def name(self) -> Text:
        return "action_search_flights"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        
        departure_city = tracker.get_slot("departure_city")
        arrival_city = tracker.get_slot("arrival_city")
        departure_date = tracker.get_slot("departure_date")
        return_date = tracker.get_slot("return_date")
        travel_class = tracker.get_slot("travel_class")
        
        # Simulated API call to fetch flight details (hardcoded for now)
        flight_options = [
            {"flight": "AI123", "airline": "Air India", "price": "$500"},
            {"flight": "UA456", "airline": "United Airlines", "price": "$550"},
        ]
        
        if departure_city and arrival_city and departure_date:
            message = f"Here are some available flights from {departure_city} to {arrival_city} on {departure_date}"
            for flight in flight_options:
                message += f"\nFlight: {flight['flight']}, Airline: {flight['airline']}, Price: {flight['price']}"
        else:
            message = "I need more details to find a flight for you. Please provide departure city, arrival city, and departure date."
        
        dispatcher.utter_message(text=message)
        
        return []

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
        message = f"You need to answer the user's question. Don't share any links to any resources or add any non-related information. Just answer the question. The user is traveling to {destination} with a {passport} passport. Here is the context of the conversation:\n\n {context}"

        # Call OpenAI function
        visa_info = openai_visa_check(passport, destination, message)

        dispatcher.utter_message(text=f"Visa requirements: {visa_info}")

        return []    

# class ActionCheckVisaRequirements(Action):
#     def name(self) -> Text:
#         return "action_check_visa_requirements"

#     def run(
#         self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]
#     ) -> List[Dict[Text, Any]]:

#         # Extracting entities (passport country and destination)
#         passport = tracker.get_slot("passport")
#         destination = tracker.get_slot("destination")

#         dispatcher.utter_message(text=f"The information is {passport} and {destination}")
#         return []
