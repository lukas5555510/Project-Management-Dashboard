from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from app.schemas.document import DocumentResponse


# POST /projects
class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None


class ProjectResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    documents: List[DocumentResponse]


class ProjectUpdate(BaseModel):
    name: str
    description: Optional[str]



