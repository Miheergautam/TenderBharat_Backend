from bson import ObjectId

async def create_or_update_profile(user_id: str, profile_data: dict, db):
    filter_ = {"user_id": ObjectId(user_id)}
    update = {"$set": profile_data}
    result = await db.profiles.update_one(filter_, update, upsert=True)
    return result

async def get_profile_by_user_id(user_id: str, db):
    profile = await db.profiles.find_one({"user_id": ObjectId(user_id)})
    if profile:
        profile["_id"] = str(profile["_id"])
        profile["user_id"] = str(profile["user_id"])
        return profile
    return None
