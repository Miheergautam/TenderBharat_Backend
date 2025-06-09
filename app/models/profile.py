from pydantic import BaseModel, Field, EmailStr, constr
from typing import List

class OfficeLocation(BaseModel):
    type: str = Field(..., example="Headquarters", description="Type of office location")
    location: str = Field(..., example="Panchkula, Haryana", description="Geographical location of the office")

class PreviousSiteInfo(BaseModel):
    location: str = Field(..., example="Dadahu, Sirmour, HP", description="Previous work site location")

class CurrentSiteInfo(BaseModel):
    location: str = Field(..., example="Dadahu, Sirmour, HP", description="Ongoing work site location")

class SiteInfo(BaseModel):
    previous_sites: List[PreviousSiteInfo] = Field(..., description="List of previous work site locations")
    current_sites: List[CurrentSiteInfo] = Field(..., description="List of ongoing work site locations")

class BridgeComfort(BaseModel):
    minor: bool = Field(..., example=True, description="Comfortable with minor bridge work")
    span_for_minor: int = Field(..., example=30, description="Maximum span for minor bridges (in meters)")
    span_for_major: int = Field(..., example=60, description="Maximum span for major bridges (in meters)")
    major: bool = Field(..., example=False, description="Comfortable with major bridge work")
    intensity: str = Field(..., example="Low", description="Comfort level or intensity for bridge work")

class TenderAmountRange(BaseModel):
    lower_limit: int = Field(..., example=50, description="Minimum preferred tender amount (in Cr)")
    upper_limit: int = Field(..., example=150, description="Maximum preferred tender amount (in Cr)")

class ProfileCreate(BaseModel):
    company_name: str = Field(..., example="Nav Bharat Construction Company", description="Legal name of the company")
    contact_person: str = Field(..., example="Rohit Sharma", description="Primary point of contact at the company")
    contact_person_email: EmailStr = Field(..., example="contact@navbharat.com", description="Email of the contact person")
    phone_number: str = Field(..., min_length=10, max_length=15, example="9876543210", description="Contact phone number")
    office_locations: List[OfficeLocation] = Field(..., description="List of company office locations")
    sites_info: List[SiteInfo] = Field(..., description="Details of current and previous work sites")
    work_types: List[str] = Field(..., example=["EPC", "Item-rate"], description="Types of tenders preferred")
    preferred_authorities: List[str] = Field(..., example=["BRO", "MORTH", "PMGSY"], description="Authorities preferred for tendering")
    bridge_work: BridgeComfort = Field(..., description="Details about bridge work comfort and limits")
    tender_amount_range: TenderAmountRange = Field(..., description="Preferred range for tender amounts")
    description: str = Field(..., example="Nav Bharat is a civil construction company focusing on hilly terrain projects.", description="Short description of the company")


