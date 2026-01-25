from .nlp import NLP
import json
from .cache import Cache
def chat():
    caller = NLP()
    print("Graph Assistant (type 'exit' to quit)")

    while True:
        user_input = input("\n> ")
        if user_input.lower() == "exit":
            break
        
        response = caller.llm_agent(user_input)
        
        # Pretty print the structured response
        if isinstance(response, dict):
            if "result" in response and isinstance(response["result"], dict):
                result = response["result"]
                if result.get("status") == "success":
                    print(f"\n✓ {json.dumps(result['data'], indent=2)}")
                else:
                    print(f"\n✗ Error: {result.get('message')}")
            else:
                print(json.dumps(response, indent=2))
        else:
            print(response)

if __name__ == "__main__":
    chat()
