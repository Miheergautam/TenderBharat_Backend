from fastapi import HTTPException
from fastapi import Request
from bson import ObjectId


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

async def get_tender_by_id(request: Request, tender_id: str):
    tenders_collection = request.app.mongodb["Tenders"]

    if not ObjectId.is_valid(tender_id):
        raise HTTPException(status_code=400, detail="Invalid Tender ID")

    tender = await tenders_collection.find_one({"_id": ObjectId(tender_id)})
    if not tender:
        raise HTTPException(status_code=404, detail="Tender not found")

    tender["_id"] = str(tender["_id"])
    if tender.get("zip_file_id"):
        tender["zip_file_id"] = str(tender["zip_file_id"])

    return tender


