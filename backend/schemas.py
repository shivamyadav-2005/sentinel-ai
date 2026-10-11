
from pydantic import BaseModel, Field


class ScanRequest(BaseModel):
    region: str = Field(min_length=1)
    scan_name: str = Field(min_length=1, max_length=100)
