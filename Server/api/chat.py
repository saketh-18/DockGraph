from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from chat.nlp import NLP

origins = ["http://localhost:3000", "https://dock-graph.vercel.app"]

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
    caller = NLP()
    response = caller.llm_agent(prompt)
    
    # Convert Pydantic model to dict for JSON serialization
    if response:
        return {
            "result": response.model_dump()
        }
    
    return {
        "result": {
            "type": "error",
            "message": "Failed to process request",
            "data": None
        }
    }
    
