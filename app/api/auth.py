
from fastapi import APIRouter, HTTPException, Depends, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2AuthorizationCodeBearer, OAuth2PasswordRequestForm
from authlib.integrations.starlette_client import OAuth
from app.models.chatbot import User
from app.db.mongo import db
from app.utils.auth import verify_password, get_password_hash, create_access_token, decode_access_token
from app.config.auth import OAUTH_CONFIGS, CALLBACK_URLS
from typing import Optional, Dict
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
from jose import JWTError, jwt

router = APIRouter()

# Initialize MongoDB collection
users = db.users

# Initialize OAuth with starlette integration
oauth = OAuth()

def setup_oauth():
    """Configure OAuth providers"""
    oauth.register(
        name='google',
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_id=OAUTH_CONFIGS["google"]["client_id"],
        client_secret=OAUTH_CONFIGS["google"]["client_secret"],
        client_kwargs={'scope': ' '.join(OAUTH_CONFIGS["google"]["scope"])}
    )

    oauth.register(
        name='facebook',
        authorize_url=OAUTH_CONFIGS["facebook"]["authorize_url"],
        access_token_url=OAUTH_CONFIGS["facebook"]["token_url"],
        client_id=OAUTH_CONFIGS["facebook"]["client_id"],
        client_secret=OAUTH_CONFIGS["facebook"]["client_secret"],
        client_kwargs={'scope': ','.join(OAUTH_CONFIGS["facebook"]["scope"])}
    )

    oauth.register(
        name='apple',
        authorize_url=OAUTH_CONFIGS["apple"]["authorize_url"],
        access_token_url=OAUTH_CONFIGS["apple"]["token_url"],
        client_id=OAUTH_CONFIGS["apple"]["client_id"],
        client_kwargs={'scope': ' '.join(OAUTH_CONFIGS["apple"]["scope"])}
    )
    return oauth

# Initialize OAuth providers
oauth = setup_oauth()

class UserInRegister(BaseModel):
    email: EmailStr
    name: Optional[str]
    password: str

class UserInResponse(BaseModel):
    id: Optional[str]
    email: EmailStr
    name: Optional[str]
    auth_provider: Optional[str]
    picture: Optional[str] = None
    provider_user_id: Optional[str] = None

@router.post("/register", response_model=UserInResponse)
async def register(user: UserInRegister):
    existing = await db["users"].find_one({"email": user.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = get_password_hash(user.password)
    user_doc = {
        "email": user.email,
        "name": user.name,
        "hashed_password": hashed_password,
        "provider": "local"
    }
    result = await db["users"].insert_one(user_doc)
    user_doc["id"] = str(result.inserted_id)
    user_doc.pop("hashed_password")
    return UserInResponse(**user_doc)

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await db["users"].find_one({"email": form_data.username})
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    access_token = create_access_token(
        data={"sub": str(user["_id"])},
        expires_delta=timedelta(minutes=60)
    )
    return {"access_token": access_token, "token_type": "bearer"}

async def get_current_user(token: str = Depends(OAuth2AuthorizationCodeBearer(
    tokenUrl="token",
    authorizationUrl="authorize"
))):
    """Get current user from JWT token"""
    try:
        user_data = decode_access_token(token)
        if user_data is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user = await users.find_one({"_id": user_data.get("sub")})
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return User(**user)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def upsert_social_user(
    provider: str,
    provider_user_id: str,
    email: str,
    name: Optional[str] = None,
    picture: Optional[str] = None
) -> User:
    """Create or update user from OAuth data"""
    user_data = {
        "email": email,
        "name": name,
        "picture": picture,
        "auth_provider": provider,
        "provider_user_id": provider_user_id
    }
    
    # Try to find existing user
    existing_user = await users.find_one({
        "auth_provider": provider,
        "provider_user_id": provider_user_id
    })
    
    if existing_user:
        # Update existing user
        await users.update_one(
            {"_id": existing_user["_id"]},
            {"$set": user_data}
        )
        user_data["id"] = existing_user["_id"]
    else:
        # Create new user
        result = await users.insert_one(user_data)
        user_data["id"] = str(result.inserted_id)
    
    return User(**user_data)

@router.get("/login/{provider}")
async def social_login(provider: str, request: Request):
    """Initialize OAuth login flow"""
    if provider not in OAUTH_CONFIGS:
        raise HTTPException(status_code=400, detail="Unsupported provider")
    
    client = oauth.create_client(provider)
    if not client:
        raise HTTPException(status_code=500, detail="OAuth client initialization failed")
    
    redirect_uri = CALLBACK_URLS[provider]
    return await client.authorize_redirect(request, redirect_uri)

@router.get("/auth/{provider}/callback")
async def auth_callback(provider: str, request: Request):
    """Handle OAuth callback"""
    if provider not in OAUTH_CONFIGS:
        raise HTTPException(status_code=400, detail="Unsupported provider")
    
    client = oauth.create_client(provider)
    if not client:
        raise HTTPException(status_code=500, detail="OAuth client initialization failed")
    
    token = await client.authorize_access_token(request)
    
    if provider == "google":
        userinfo = token.get('userinfo')
        if userinfo:
            user = await upsert_social_user(
                provider="google",
                provider_user_id=userinfo['sub'],
                email=userinfo['email'],
                name=userinfo.get('name'),
                picture=userinfo.get('picture')
            )
    elif provider == "facebook":
        client = oauth.create_client('facebook')
        if not client:
            raise HTTPException(status_code=500, detail="Facebook client initialization failed")
        
        resp = await client.get('me', token=token, params={'fields': 'id,email,name,picture'})
        userinfo = resp.json()
        user = await upsert_social_user(
            provider="facebook",
            provider_user_id=userinfo['id'],
            email=userinfo['email'],
            name=userinfo.get('name'),
            picture=userinfo.get('picture', {}).get('data', {}).get('url')
        )
    elif provider == "apple":
        # Apple specific handling
        userinfo = token.get('userinfo', {})
        user = await upsert_social_user(
            provider="apple",
            provider_user_id=userinfo['sub'],
            email=userinfo['email'],
            name=token.get('user', {}).get('name', {}).get('firstName')
        )
    
    # Create access token
    access_token = create_access_token({"sub": str(user.id)})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

@router.get("/me", response_model=UserInResponse)
async def read_users_me(current_user: UserInResponse = Depends(get_current_user)):
    return current_user

# Health check endpoint
@router.get("/health")
async def health_check():
    return {"status": "healthy"}
