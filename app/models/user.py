from pydantic import BaseModel, EmailStr
from typing import Optional

class User(BaseModel):
    id: Optional[str]
    email: EmailStr
    name: Optional[str]
    hashed_password: Optional[str]
    provider: Optional[str]  # 'local', 'google', 'facebook'
