from fastapi import APIRouter, HTTPException
from app.models.enquiry import Enquiry
from app.db.mongo import db
from typing import List

router = APIRouter()

@router.get("/", response_model=List[Enquiry])
async def list_enquiries():
    enquiries = []
    async for enquiry in db["enquiries"].find():
        enquiry["id"] = str(enquiry["_id"])
        enquiry.pop("_id")
        enquiries.append(Enquiry(**enquiry))
    return enquiries

@router.post("/", response_model=Enquiry)
async def create_enquiry(enquiry: Enquiry):
    enquiry_dict = enquiry.dict(exclude_unset=True)
    result = await db["enquiries"].insert_one(enquiry_dict)
    enquiry_dict["id"] = str(result.inserted_id)
    return Enquiry(**enquiry_dict)
