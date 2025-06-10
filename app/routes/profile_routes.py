from fastapi import APIRouter, Request, HTTPException
from app.models.profile import ProfileCreate , ProfileUpdate
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
            elif isinstance(v, (dict, list)):
                new_doc[k] = serialize_mongo_document(v)
            else:
                new_doc[k] = v
        return new_doc
    return doc


async def get_user_obj_id_from_token(request: Request) -> ObjectId:
    token = request.cookies.get("token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    user_id = auth_controller.decode_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    try:
        return ObjectId(user_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid user ID format")


@router.post("/profile")
async def create_profile(request: Request, data: ProfileCreate):
    try:
        db = request.app.mongodb
        user_obj_id = await get_user_obj_id_from_token(request)

        user = await db.users.find_one({"_id": user_obj_id})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        existing_profile = await profile_controller.get_profile_by_user_id(str(user_obj_id), db)
        if existing_profile:
            raise HTTPException(status_code=400, detail="Profile already exists")

        profile_data = data.model_dump()
        profile_data["user_id"] = user_obj_id
        result = await db.profiles.insert_one(profile_data)

        return {"message": "Profile created successfully", "profile_id": str(result.inserted_id)}

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


@router.get("/profile")
async def get_profile(request: Request):
    try:
        db = request.app.mongodb
        user_obj_id = await get_user_obj_id_from_token(request)

        user = await db.users.find_one({"_id": user_obj_id})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        profile = await profile_controller.get_profile_by_user_id(str(user_obj_id), db)
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")

        return serialize_mongo_document(profile)

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


""" @router.put("/profile")
async def update_profile(request: Request, data: ProfileUpdate):
    try:
        db = request.app.mongodb
        user_obj_id = await get_user_obj_id_from_token(request)

        user = await db.users.find_one({"_id": user_obj_id})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        existing_profile = await profile_controller.get_profile_by_user_id(str(user_obj_id), db)
        if not existing_profile:
            raise HTTPException(status_code=404, detail="Profile not found")

        await profile_controller.create_or_update_profile(str(user_obj_id), data.model_dump(), db)
        return {"message": "Profile updated successfully"}

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
 """

@router.put("/profile")
async def update_profile(request: Request, data: ProfileUpdate):
    try:
        db = request.app.mongodb
        user_obj_id = await get_user_obj_id_from_token(request)

        # Get only the fields that were provided (ignore None values)
        update_data = data.model_dump(exclude_unset=True, exclude_none=True)

        if not update_data:
            raise HTTPException(status_code=400, detail="No valid fields provided for update")

        result = await db.profiles.update_one(
            {"user_id": user_obj_id},
            {"$set": update_data}
        )

        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Profile not found")

        return {"message": "Profile updated successfully"}

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")