from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
# import openai  # Uncomment if using OpenAI

router = APIRouter()

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

# Placeholder for OpenAI integration
@router.post("/", response_model=ChatResponse)
async def ask_chatbot(request: ChatRequest):
    # Uncomment and implement with OpenAI if desired
    # openai.api_key = os.getenv("OPENAI_API_KEY")
    # response = openai.ChatCompletion.create(...)
    # return ChatResponse(response=response['choices'][0]['message']['content'])
    return ChatResponse(response=f"Echo: {request.message}")
