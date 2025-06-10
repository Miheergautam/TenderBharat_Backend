from fastapi import Request, HTTPException
from bson import ObjectId
from app.models.compatibility import CompatibilityRecord
from app.controllers import auth_controller

# ---------- helpers ---------- #
def _serialize(doc: dict) -> dict:
    doc["_id"] = str(doc["_id"])
    doc["user_id"] = str(doc["user_id"])
    doc["tender_id"] = str(doc["tender_id"])
    return doc

def _validate_object_id(oid: str, field: str):
    if not ObjectId.is_valid(oid):
        raise HTTPException(status_code=400, detail=f"Invalid {field}")

def _get_user_id_from_cookie(request: Request) -> str:
    token = request.cookies.get("token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    user_id = auth_controller.decode_token(token)
    if not user_id or not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return user_id

# ---------- CRUD functions ---------- #
async def create_compatibility_record(request: Request, payload: CompatibilityRecord):
    """Insert a new compatibility record (auth enforced)."""
    user_id = _get_user_id_from_cookie(request)
    _validate_object_id(payload.tender_id, "tender_id")

    collection = request.app.mongodb["Compatibility"]

    duplicate = await collection.find_one({
        "user_id": ObjectId(user_id),
        "tender_id": ObjectId(payload.tender_id)
    })
    if duplicate:
        raise HTTPException(status_code=409, detail="Record already exists")

    record = {
        "user_id": ObjectId(user_id),
        "tender_id": ObjectId(payload.tender_id),
        "compatibility_score": payload.compatibility_score,
        "compatibility_analysis": payload.compatibility_analysis,
    }
    result = await collection.insert_one(record)
    return {"message": "Record created", "id": str(result.inserted_id)}

async def get_all_records(request: Request):
    """Return all records – auth enforced."""
    """ _ = _get_user_id_from_cookie(request) """
    collection = request.app.mongodb["Compatibility"]
    return [_serialize(d) async for d in collection.find()]

async def get_by_user_and_tender(request: Request, user_id: str, tender_id: str):
    """Return record filtered by user_id AND tender_id – auth enforced."""
    _ = _get_user_id_from_cookie(request)
    _validate_object_id(user_id, "user_id")
    _validate_object_id(tender_id, "tender_id")

    collection = request.app.mongodb["Compatibility"]
    doc = await collection.find_one({
        "user_id": ObjectId(user_id),
        "tender_id": ObjectId(tender_id)
    })
    if not doc:
        raise HTTPException(status_code=404, detail="Record not found")
    return _serialize(doc)

async def get_by_user(request: Request, user_id: str):
    """All records for one user – auth enforced."""
    _ = _get_user_id_from_cookie(request)
    _validate_object_id(user_id, "user_id")
    collection = request.app.mongodb["Compatibility"]
    return [_serialize(d) async for d in collection.find({"user_id": ObjectId(user_id)})]

async def get_by_tender(request: Request, tender_id: str):
    """All records for one tender – auth enforced."""
    _ = _get_user_id_from_cookie(request)
    _validate_object_id(tender_id, "tender_id")
    collection = request.app.mongodb["Compatibility"]
    return [_serialize(d) async for d in collection.find({"tender_id": ObjectId(tender_id)})]
