from pydantic import BaseModel, Field
from typing import Optional

class Trip(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    title: str
    image: str
    date: str
    duration: str
    description: str
    details: str
