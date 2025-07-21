# Travel Site Backend (FastAPI + MongoDB Atlas)

This is the backend for the travel website, built with FastAPI and using MongoDB Atlas as the database.

## Features
- User authentication (direct, Google, Facebook)
- CRUD for trips (past/future)
- Enquiries/suggestions
- Chatbot integration (OpenAI, bookings.com, Skyscanner)
- Itinerary PDF generation
- Search history

## Setup
1. Create a virtual environment:
   ```sh
   python3 -m venv venv
   source venv/bin/activate
   ```
2. Install dependencies:
   ```sh
   pip install fastapi uvicorn motor pymongo python-jose[cryptography] passlib[bcrypt] python-dotenv requests
   ```
3. Create a `.env` file with your MongoDB Atlas URI and any API keys needed.
4. Run the server:
   ```sh
   uvicorn app.main:app --reload
   ```

## Project Structure
- `app/main.py`: FastAPI entrypoint
- `app/api/`: API routers (trips, auth, chatbot, etc.)
- `app/models/`: Pydantic models
- `app/db/`: Database connection and helpers
- `app/utils/`: Utility functions (PDF, OpenAI, etc.)

---
Replace placeholder code and secrets before deploying to production.
