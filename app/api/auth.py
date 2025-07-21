
from fastapi import APIRouter, HTTPException, Depends, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.models.user import User
from app.db.mongo import db
from app.utils.auth import verify_password, get_password_hash, create_access_token, decode_access_token
from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import timedelta

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

class UserInRegister(BaseModel):
    email: EmailStr
    name: Optional[str]
    password: str

class UserInResponse(BaseModel):
    id: Optional[str]
    email: EmailStr
    name: Optional[str]
    provider: Optional[str]

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
        data={"sub": user["email"]},
        expires_delta=timedelta(minutes=60)
    )
    return {"access_token": access_token, "token_type": "bearer"}

async def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    user = await db["users"].find_one({"email": payload["sub"]})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user["id"] = str(user["_id"])
    user.pop("_id")
    user.pop("hashed_password", None)
    return UserInResponse(**user)

@router.get("/me", response_model=UserInResponse)
async def read_users_me(current_user: UserInResponse = Depends(get_current_user)):
    return current_user

# Placeholder for OAuth endpoints (Google, Facebook)
@router.get("/oauth/{provider}")
async def oauth_login(provider: str):
    return {"msg": f"OAuth login for {provider} not implemented yet."}
