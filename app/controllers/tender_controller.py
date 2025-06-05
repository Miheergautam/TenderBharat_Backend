from fastapi import HTTPException
from fastapi import Request

async def get_all_tenders(request: Request):
    tenders_collection = request.app.mongodb["Tenders"]
    cursor = tenders_collection.find({})
    tenders = []
    async for tender in cursor:
        tender["_id"] = str(tender["_id"])
        if tender.get("zip_file_id"):
            tender["zip_file_id"] = str(tender["zip_file_id"])
        tenders.append(tender)
    return tenders


