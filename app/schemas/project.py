from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from app.schemas.document import DocumentResponse


# POST /projects
class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None


# GET /projects (list)
class ProjectListResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    owner_id: int
    created_at: datetime
    documents: List["DocumentResponse"] = []


class ProjectResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]


class ProjectUpdate(BaseModel):
    name: str
    description: Optional[str]



