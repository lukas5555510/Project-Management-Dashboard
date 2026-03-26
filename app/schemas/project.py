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


# GET /project/<project_id>/info
class ProjectResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    owner_id: int
    created_at: datetime


# PUT /project/<project_id>/info
class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    owner_id: Optional[int] = None


# DELETE /project/<project_id>
class ProjectDelete(BaseModel):
    message: str

#POST /project/<project_id>/invite?user=<login>
class GrantProjectAccessRequest(BaseModel):
    user_login: str