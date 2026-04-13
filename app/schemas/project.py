from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from app.schemas.document import DocumentResponse


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
    documents: List[DocumentResponse] = []

    model_config = ConfigDict(from_attributes=True)

class ProjectDeleteResponse(BaseModel):
    success: bool
    message: str
    deleted_id: int

class InvitingToProjectResponse(BaseModel):
    message: str
    project_id: int
    login: str

class InvitingToProjectRequest(BaseModel):
    login: str

