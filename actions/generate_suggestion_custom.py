from typing import Any, Text, Dict, List
from actions.generate_suggestions import ActionGenerateSuggestions

class ActionGenerateSuggestionsCustom(ActionGenerateSuggestions):

    def name(self) -> Text:
        return "action_generate_suggestions_custom"

    def get_suggestion_list(self):
        suggestions = [
        "Search flights - I want to search for flights",
        "Visa requirements - I want to check visa requirements",
        "Upgrade seats - How to upgrade my seats",
        "Cancel reservation - How to cancel reservation",
        "Change reservation - How to change reservation",
        "Change flight - How to change flight",
        "Pet policy - What is the pet policy",
        "Refund policy - What is the refund policy",
        "Cancellation policy - What is the cancellation policy"
    ]
        return suggestions
    
    def get_suggestion_message(self):
        return "Is there anything else I can assist you with?"