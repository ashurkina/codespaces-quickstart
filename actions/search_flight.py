from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher


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