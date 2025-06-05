from pydantic import BaseModel, Field
from pydantic import TypeAdapter, ValidationError
from typing import Optional, List
from bson import ObjectId


class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(cls, _source_type, _handler):
        from pydantic import core_schema

        def validate(v):
            if not ObjectId.is_valid(v):
                raise ValueError(f"Invalid ObjectId: {v}")
            return ObjectId(v)

        return core_schema.no_info_after_validator_function(validate)


class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_json_schema__(cls, _schema):
        return {"type": "string"}

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError(f"Invalid ObjectId: {v}")
        return ObjectId(v)


class TenderMetadata(BaseModel):
    Terrain: Optional[str]
    Climate: Optional[str]
    Logistics: Optional[str]
    Safety: Optional[str]
    Soil_Type: Optional[str] = Field(alias="Soil Type")
    Material_Availability: Optional[str] = Field(alias="Material Availability")
    Roadside_Drainage: Optional[str] = Field(alias="Roadside Drainage")
    Structures_Work: Optional[str] = Field(alias="Structures Work")
    Location_Images: Optional[List[str]] = Field(default=None, alias="Location Images")

    model_config = {
        "validate_by_name": True,
    }


class Tender(BaseModel):
    id: str
    Bio: str
    Location: str = Field(alias="Location")
    Submission_Date: str = Field(alias="Submission Date")
    EMD: str
    Organization: str
    Organization_Tender_ID: str = Field(alias="Organization Tender ID")
    Website: str
    Download_Documents: str = Field(alias="Download Documents")
    Length: str
    Type: str
    metadata: TenderMetadata
    zip_file_id: Optional[PyObjectId] = None

    model_config = {
        "validate_by_name": True,
        "json_encoders": {ObjectId: str},
        "arbitrary_types_allowed": True,
    }
