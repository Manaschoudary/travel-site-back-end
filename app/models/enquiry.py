from pydantic import BaseModel
from typing import Optional

class Enquiry(BaseModel):
    id: Optional[str]
    name: str
    email: str
    message: str
