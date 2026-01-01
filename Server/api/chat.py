from chat.executor import Executor
from chat.formatter import format_response
from chat.nlp import parse_intent
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

origins = ["http://localhost:3000"]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)



@app.post("/chat")
def handle_chat(prompt: str):
    context = {}
    intent = parse_intent(prompt, context)
    
    if intent["intent"] == "unknown":
        return {
            "result" : "I'm not sure what you mean. Can you clarify?"
        }
        
    executor = Executor();
    result = executor.execute(intent);
    response = format_response(intent, result)
    
    print(response);
    
    context["last_entity"] = intent.get("entity_name")
    context["last_entity_type"] = intent.get("entity_type")
    context["last_intent"] = intent.get("intent")
    
    
    return {
        "result" : response
    }
    
