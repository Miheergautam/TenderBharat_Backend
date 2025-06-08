from pydantic import BaseModel, Field
from typing import List

class OfficeLocation(BaseModel):
    type: str = Field(..., example="Headquarters")  
    location: str = Field(..., example="Panchkula, Haryana")

class SiteInfo(BaseModel):
    name: str = Field(..., example="PMGSY Road Project 20Cr")
    value: str = Field(..., example="Road Project")
    location: str = Field(..., example="Dadahu, Sirmour, HP")

class PreferredTender(BaseModel):
    work: str = Field(..., example="Road Construction")
    mode_order: List[str] = Field(..., example=["EPC", "Item-rate"])
    authority: List[str] = Field(..., example=["BRO", "MORTH", "PMGSY"])
    amount_range_cr: str = Field(..., example="₹50–150 Cr preferred")

class BridgeComfort(BaseModel):
    minor: bool = Field(..., example=True)
    span_up_to_m: int = Field(..., example=30)
    major: bool = Field(..., example=False)
    comfort_level: str = Field(..., example="Low")

class ProfileCreate(BaseModel):
    company_name: str = Field(..., example="Nav Bharat Construction Company")
    office_locations: List[OfficeLocation]
    ongoing_sites: List[SiteInfo]
    previous_works: List[str] = Field(..., example=["50 Cr Road Works in Sirmour, HP"])
    preferred_tender: PreferredTender
    bridge_work: BridgeComfort