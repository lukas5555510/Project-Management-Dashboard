from fastapi import APIRouter, Path, Query
from typing import List
from app.schemas.project import (
    ProjectCreate, ProjectListResponse,
    ProjectResponse, ProjectUpdate, ProjectDelete
)
from app.schemas.document import ProjectDocumentListResponse, ProjectDocumentUpload
from app.schemas.project import GrantProjectAccessRequest

router = APIRouter()

@router.post("/projects", response_model=ProjectResponse)
def create_project(project: ProjectCreate):
    # create project, assign owner
    ...

@router.get("/projects", response_model=List[ProjectListResponse])
def list_projects():
    # return projects accessible by user
    ...

@router.get("/project/{project_id}/info", response_model=ProjectResponse)
def get_project_info(project_id: int = Path(...)):
    ...

@router.put("/project/{project_id}/info", response_model=ProjectResponse)
def update_project(project_id: int, project: ProjectUpdate):
    ...

@router.delete("/project/{project_id}", response_model=ProjectDelete)
def delete_project(project_id: int):
    ...