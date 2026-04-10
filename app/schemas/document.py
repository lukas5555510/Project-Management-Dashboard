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

    class Config:
        from_attributes = True

class DocumentUpdate(BaseModel):
    s3_path: str
    project_id: int


class DocumentSchema(BaseModel):
    id: int
    s3_path: str
    project_id: int

    class Config:
        from_attributes = True