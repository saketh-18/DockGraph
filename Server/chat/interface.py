from .nlp import parse_intent
from .executor import Executor
from .formatter import format_response

def chat():
    executor = Executor()
    context = {}

    print("Graph Assistant (type 'exit' to quit)")

    while True:
        user_input = input("\n> ")
        if user_input.lower() == "exit":
            break

        intent = parse_intent(user_input, context)

        if intent["intent"] == "unknown":
            print("I'm not sure what you mean. Can you clarify?")
            continue

        result = executor.execute(intent)
        response = format_response(intent, result)
        print(response)

        # Update context
        context["last_entity"] = intent.get("entity_name")
        context["last_entity_type"] = intent.get("entity_type")
        context["last_intent"] = intent.get("intent")

if __name__ == "__main__":
    chat()
