from pydantic import BaseModel, Field
from typing import Any

class CompatibilityRecord(BaseModel):
    tender_id: str = Field(..., description="Tender ID (as string)")
    compatibility_score: float = Field(..., ge=0, le=100, description="Compatibility score (0 to 1)")
    compatibility_analysis: str = Field(..., description="Markdown-formatted analysis")
