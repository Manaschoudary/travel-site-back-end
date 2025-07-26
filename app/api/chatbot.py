from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

# Initialize OpenAI client
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

# Travel assistant prompt template
TRAVEL_ASSISTANT_PROMPT = """
You are a friendly and knowledgeable travel assistant for a travel booking website. Your role is to:

1. Help users plan their trips and provide travel advice
2. Suggest destinations, activities, and travel tips
3. Answer questions about travel requirements, weather, culture, and local attractions
4. Assist with general travel planning and booking inquiries
5. Be enthusiastic and helpful while maintaining a professional tone

Guidelines:
- Always be helpful, friendly, and informative
- Provide practical and actionable travel advice
- If you don't know specific current information (like real-time prices or availability), suggest they check the website or contact customer service
- Keep responses concise but informative
- Focus on travel-related topics

User's message: {user_message}

Please provide a helpful travel-focused response:
"""

@router.post("/", response_model=ChatResponse)
async def ask_chatbot(request: ChatRequest):
    try:
        # Check if OpenAI API key is configured
        if not os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY") == "your_openai_key":
            return ChatResponse(response="Travel Assistant: I'm currently not configured with an OpenAI API key. Please contact support for assistance with your travel questions!")
        
        # Create the prompt with user message
        prompt = TRAVEL_ASSISTANT_PROMPT.format(user_message=request.message)
        
        # Make OpenAI API call
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful travel assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        ai_response = response.choices[0].message.content
        if ai_response:
            ai_response = ai_response.strip()
        else:
            ai_response = "I'm sorry, I couldn't generate a response. Please try again!"
        return ChatResponse(response=ai_response)
        
    except Exception as e:
        # Fallback response in case of API errors
        return ChatResponse(response=f"Travel Assistant: I'm having trouble connecting right now, but I'd love to help with your travel questions! Please try again in a moment or contact our support team for immediate assistance.")
