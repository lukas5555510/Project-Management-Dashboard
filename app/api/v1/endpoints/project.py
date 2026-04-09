from typing import List

from fastapi import APIRouter, Depends, HTTPException

from app.core.security import get_current_user_id
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse
from app.services.project_service import ProjectService

router = APIRouter()

@router.post("/projects", response_model=ProjectResponse)
def create_project(
        project: ProjectCreate,
        user_id: int = Depends(get_current_user_id),
        project_service: ProjectService = Depends()
):
    return project_service.create_project(user_id, project)

@router.get("/projects", response_model=List[ProjectResponse])
def get_projects(
        project_service: ProjectService = Depends(),
        user_id: int = Depends(get_current_user_id)
):
    return project_service.get_projects_for_user(user_id)

@router.get("/project/{project_id}/info")
def get_project_info(
        project_id: int, project_service: ProjectService = Depends(),
        user_id: int = Depends(get_current_user_id)
):
    return project_service.get_project_info(project_id)

@router.put("/project/{project_id}/info", response_model=ProjectUpdate)
def update_project_info(
        project_id: int,
        project: ProjectUpdate,
        project_service: ProjectService = Depends(),
        user_id: int = Depends(get_current_user_id)
):
    return project_service.update_project_info(project_id, project)

@router.delete("/project/{project_id}")
def delete_project(
        project_id: int,
        project_service: ProjectService = Depends(),
        user_id: int = Depends(get_current_user_id)
):
    return project_service.delete_project(project_id)

@router.post("/project/{project_id}/invite")
def invite_user_to_project(
    project_id: int,
    user: str,  # query parameter
    user_id: int = Depends(get_current_user_id),  # optional: require authentication
    project_service: ProjectService = Depends()
):
    return project_service.grant_access_to_project(project_id, user_id, user)