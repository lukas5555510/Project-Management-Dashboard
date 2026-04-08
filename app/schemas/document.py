from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class DocumentCreate(BaseModel):
    s3_path: str
    project_id: int

# GET /document/<document_id>
class DocumentResponse(BaseModel):
    id: int
    s3_path: str
    project_id: int

    model_config = {
        "from_attributes": True  # Enables ORM conversion in Pydantic v2
    }

    class Config:
        orm_mode = True

class DocumentUpdate(BaseModel):
    s3_path: str
    project_id: int