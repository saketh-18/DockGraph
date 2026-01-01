# we get user input
# create a schema to translate user input into queries

import json
import pprint
from typing import Dict
import api
from groq import Groq
import os
from dotenv import load_dotenv

# This looks for a .env file in the current directory
load_dotenv()
groq_api_key = os.getenv("groq_api_key")

pp = pprint.PrettyPrinter(indent=4);
client = Groq(api_key=groq_api_key)

def parse_intent(user_input : str, context : Dict) -> Dict:

    chat_completion = client.chat.completions.create(
        model="openai/gpt-oss-safeguard-20b",
        messages=[
            {
                "role":"system",
                "content": 
                    """
                You are an intent classifier for a graph query system.
    Your job is to translate a user question into a structured JSON command.

    The system supports ONLY these intents:
    - get_owner
    - get_owned_by_team
    - list_nodes
    - downstream
    - upstream
    - blast_radius
    - path
    - follow_up
    - unknown

    Graph entity types:
    - service
    - database
    - cache
    - team

    Valid entity names:
    ['api-gateway', 'auth-service', 'order-service', 'payment-service',
    'inventory-service', 'notification-service', 'recommendation-service',
    'users-db', 'orders-db', 'payments-db', 'inventory-db',
    'redis-main',
    'platform-team', 'identity-team', 'orders-team', 'payments-team', 'ml-team']

    Rules:
    1. Always return valid JSON and nothing else.
    2. Correct minor spelling mistakes and map to the closest valid entity name.
    3. Infer entity type from the entity name.
    4. If the user asks a follow-up using pronouns ("it", "that", "what about X"),
    return intent = "follow_up".
    5. If the question cannot be answered using the graph, return intent = "unknown".
    6. NEVER invent entities.
    8. Ownership questions always map to get_owner or list_nodes (never invent intents).
    9. Give from and to entity name and type if asked something related to path.
    10. If nothing related to path is asked dont include path in the result
     
    give downstream if asked about on whom i depend on, 
    give upstream if asked about who depends on me.

    JSON output format:

    {
    "intent": "<intent>",
    "entity_name":"<entity_name>",
    "entity_type": "<entity_type>",
    "path" : {
        "from_type" : <entity_type>,
        "from_name" : <entity_name>,
        "to_type" : <entity_type>,
        "to_name" : <entity_name>
    }
    "filters": "<entity_type>" | null
    }
    """},
            {
                "role": "user",
                "content" : f"{user_input}"
            }
        ]
    )
    
    try:
        response = chat_completion.choices[0].message.content;
        intent = json.loads(response)
        # print("groq response");
        # pp.pprint(intent);
    except Exception:
        return {"intent": "unknown", "reason": "invalid model output"}
    
    if intent.get("intent") == "unknown" and context.get("last_entity"):
        intent["entity_name"] = context["last_entity"]
        intent["entity_type"] = context.get("last_entity_type")
        intent["intent"] = context.get("last_intent", "unknown")
    
    if intent.get("intent") == "follow_up" and context.get("last_entity"):
        intent["intent"] = context.get("last_intent");
        
    return intent