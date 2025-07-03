from app.services.robo import tender_service
import certifi
import json
from fastapi import Request

async def process_query_controller(user_query: str, request: Request):
    result = tender_service.process_user_query(user_query)
    try:
        mongo_filter = json.loads(result)
    except Exception as e:
        raise ValueError(f"❌ Could not parse Mongo filter: {e}")
    
    try:
        # use the app’s mongo db
        tenders_collection = request.app.mongodb["Test"]
        
        cursor = tenders_collection.find(mongo_filter)
        tenders = await cursor.to_list(length=100)
        
        if not tenders:
            return "No tenders found for this filter."
        
        # Convert ObjectId to string
        for tender in tenders:
            tender["_id"] = str(tender["_id"])
            
        return tenders
    
    except Exception as e:
        raise ValueError(f"❌ Error searching Mongo: {e}")

