from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from app.schemas.document import DocumentResponse, DocumentSchema


# POST /projects
class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
class ProjectUpdate(BaseModel):
    name: str
    description: Optional[str]

class ProjectResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    documents: List[DocumentSchema] = []

    class Config:
        from_attributes = True

class ProjectDeleteResponse(BaseModel):
    success: bool
    message: str
    deleted_id: int


