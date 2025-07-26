
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import trips, enquiries, auth, chatbot
from app.api import pdf

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Routers

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(trips.router, prefix="/trips", tags=["trips"])
app.include_router(enquiries.router, prefix="/enquiries", tags=["enquiries"])
app.include_router(chatbot.router, prefix="/chatbot", tags=["chatbot"])
app.include_router(pdf.router, prefix="/pdf", tags=["pdf"])

@app.get("/")
def root():
    return {"message": "Travel Site Backend is running!"}
