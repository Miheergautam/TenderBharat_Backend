from fastapi import APIRouter, Request, HTTPException
from app.models.profile import ProfileCreate
from app.controllers import profile_controller, auth_controller
from bson import ObjectId

router = APIRouter()

def serialize_mongo_document(doc):
    if isinstance(doc, list):
        return [serialize_mongo_document(d) for d in doc]
    elif isinstance(doc, dict):
        new_doc = {}
        for k, v in doc.items():
            if isinstance(v, ObjectId):
                new_doc[k] = str(v)
            elif isinstance(v, dict) or isinstance(v, list):
                new_doc[k] = serialize_mongo_document(v)
            else:
                new_doc[k] = v
        return new_doc
    else:
        return doc

async def get_user_obj_id_from_token(request: Request) -> ObjectId:
    token = request.cookies.get("token")
    print("token",token)
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    user_id = auth_controller.decode_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    try:
        user_obj_id = ObjectId(user_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid user ID format")
    return user_obj_id

@router.post("/profile")
async def create_profile(request: Request, data: ProfileCreate):
    db = request.app.mongodb
    print("inside function")
    user_obj_id = await get_user_obj_id_from_token(request)

    # Check if user exists
    user = await db.users.find_one({"_id": user_obj_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if profile already exists
    existing_profile = await profile_controller.get_profile_by_user_id(str(user_obj_id), db)
    if existing_profile:
        raise HTTPException(status_code=400, detail="Profile already exists for this user")

    # Insert new profile (don't upsert)
    profile_data = data.dict()
    profile_data["user_id"] = user_obj_id
    result = await db.profiles.insert_one(profile_data)

    return {
        "message": "Profile created successfully",
        "profile_id": str(result.inserted_id)
    }


@router.get("/profile")
async def get_profile(request: Request):
    db = request.app.mongodb
    user_obj_id = await get_user_obj_id_from_token(request)

    # Check if user exists
    user = await db.users.find_one({"_id": user_obj_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    profile = await profile_controller.get_profile_by_user_id(str(user_obj_id), db)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    return serialize_mongo_document(profile)

@router.put("/profile")
async def update_profile(request: Request, data: ProfileCreate):
    db = request.app.mongodb
    user_obj_id = await get_user_obj_id_from_token(request)

    # Check if user exists
    user = await db.users.find_one({"_id": user_obj_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if profile exists before update (optional)
    existing_profile = await profile_controller.get_profile_by_user_id(str(user_obj_id), db)
    if not existing_profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    # Full replacement update
    await profile_controller.create_or_update_profile(str(user_obj_id), data.dict(), db)
    return {"message": "Profile updated successfully"}
