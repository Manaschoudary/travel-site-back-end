import os
from typing import Dict
from dotenv import load_dotenv

load_dotenv()

# OAuth2 configuration
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
FACEBOOK_CLIENT_ID = os.getenv("FACEBOOK_CLIENT_ID")
FACEBOOK_CLIENT_SECRET = os.getenv("FACEBOOK_CLIENT_SECRET")
APPLE_CLIENT_ID = os.getenv("APPLE_CLIENT_ID")
APPLE_TEAM_ID = os.getenv("APPLE_TEAM_ID")
APPLE_KEY_ID = os.getenv("APPLE_KEY_ID")
APPLE_PRIVATE_KEY = os.getenv("APPLE_PRIVATE_KEY")

# JWT configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

# Frontend URLs
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

# OAuth configurations
OAUTH_CONFIGS: Dict = {
    "google": {
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "authorize_url": "https://accounts.google.com/o/oauth2/v2/auth",
        "token_url": "https://oauth2.googleapis.com/token",
        "userinfo_url": "https://www.googleapis.com/oauth2/v3/userinfo",
        "scope": ["openid", "email", "profile"],
    },
    "facebook": {
        "client_id": FACEBOOK_CLIENT_ID,
        "client_secret": FACEBOOK_CLIENT_SECRET,
        "authorize_url": "https://www.facebook.com/v12.0/dialog/oauth",
        "token_url": "https://graph.facebook.com/v12.0/oauth/access_token",
        "userinfo_url": "https://graph.facebook.com/me",
        "scope": ["email", "public_profile"],
    },
    "apple": {
        "client_id": APPLE_CLIENT_ID,
        "team_id": APPLE_TEAM_ID,
        "key_id": APPLE_KEY_ID,
        "private_key": APPLE_PRIVATE_KEY,
        "authorize_url": "https://appleid.apple.com/auth/authorize",
        "token_url": "https://appleid.apple.com/auth/token",
        "scope": ["name", "email"],
    }
}

# Callback URLs
CALLBACK_URLS = {
    "google": f"{FRONTEND_URL}/auth/google/callback",
    "facebook": f"{FRONTEND_URL}/auth/facebook/callback",
    "apple": f"{FRONTEND_URL}/auth/apple/callback"
}
