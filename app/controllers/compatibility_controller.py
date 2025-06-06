from fastapi import Request, HTTPException
from bson import ObjectId
from app.models.compatibility import CompatibilityRecord

# Helper function to serialize ObjectId
def _serialize(doc: dict) -> dict:
    doc["_id"] = str(doc["_id"])
    doc["tender_id"] = str(doc["tender_id"])
    return doc

# POST /compatibility
async def create_compatibility_record(request: Request, payload: CompatibilityRecord):
    if not ObjectId.is_valid(payload.tender_id):
        raise HTTPException(status_code=400, detail="Invalid tender_id")

    collection = request.app.mongodb["Compatibility"]

    # Check if record already exists for the tender
    existing = await collection.find_one({"tender_id": ObjectId(payload.tender_id)})
    if existing:
        raise HTTPException(status_code=409, detail="Record already exists for this tender_id")

    record = {
        "tender_id": ObjectId(payload.tender_id),
        "compatibility_score": payload.compatibility_score,
        "compatibility_analysis": payload.compatibility_analysis,
    }

    result = await collection.insert_one(record)

    return {
        "message": "Compatibility record created",
        "id": str(result.inserted_id),
    }

# GET /compatibility
async def get_all_compatibility_records(request: Request):
    collection = request.app.mongodb["Compatibility"]
    cursor = collection.find()
    records = []

    async for doc in cursor:
        records.append(_serialize(doc))

    return records

# GET /compatibility/{tender_id}
async def get_compatibility_by_tender(request: Request, tender_id: str):
    if not ObjectId.is_valid(tender_id):
        raise HTTPException(status_code=400, detail="Invalid tender_id")

    collection = request.app.mongodb["Compatibility"]
    doc = await collection.find_one({"tender_id": ObjectId(tender_id)})

    if not doc:
        raise HTTPException(status_code=404, detail="Compatibility record not found")

    return _serialize(doc)
