from fastapi import APIRouter, Depends, HTTPException
from app.schemas.project import ProjectCreate, ProjectUpdate
from app.services.project_service import ProjectService

router = APIRouter()

@router.post("/projects", response_model=ProjectCreate)
async def create_project(project: ProjectCreate, project_service: ProjectService = Depends()):
    return await project_service.create_project(project)

@router.get("/projects")
async def get_projects(project_service: ProjectService = Depends()):
    return await project_service.get_projects()

@router.get("/project/{project_id}/info")
async def get_project_info(project_id: int, project_service: ProjectService = Depends()):
    return await project_service.get_project_info(project_id)

@router.put("/project/{project_id}/info", response_model=ProjectUpdate)
async def update_project_info(project_id: int, project: ProjectUpdate, project_service: ProjectService = Depends()):
    return await project_service.update_project_info(project_id, project)

@router.delete("/project/{project_id}")
async def delete_project(project_id: int, project_service: ProjectService = Depends()):
    return await project_service.delete_project(project_id)