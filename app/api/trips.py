from fastapi import APIRouter, HTTPException
from app.models.trip import Trip
from app.db.mongo import db
from typing import List
from bson import ObjectId

router = APIRouter()

@router.get("/", response_model=List[Trip])
async def list_trips():
    trips = []
    async for trip in db["trips"].find():
        trip["id"] = str(trip["_id"])
        trip.pop("_id")
        trips.append(Trip(**trip))
    return trips

@router.post("/", response_model=Trip)
async def create_trip(trip: Trip):
    trip_dict = trip.dict(exclude_unset=True)
    result = await db["trips"].insert_one(trip_dict)
    trip_dict["id"] = str(result.inserted_id)
    return Trip(**trip_dict)

@router.get("/{trip_id}", response_model=Trip)
async def get_trip(trip_id: str):
    trip = await db["trips"].find_one({"_id": ObjectId(trip_id)})
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    trip["id"] = str(trip["_id"])
    trip.pop("_id")
    return Trip(**trip)

@router.delete("/{trip_id}")
async def delete_trip(trip_id: str):
    result = await db["trips"].delete_one({"_id": ObjectId(trip_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Trip not found")
    return {"msg": "Trip deleted"}
