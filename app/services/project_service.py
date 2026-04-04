from typing import List
from sqlalchemy.orm import Session

from app.repositories.project_repository import ProjectRepository
from app.schemas.project import ProjectCreate, ProjectUpdate
from app.core.exceptions import PermissionDenied, NotFoundError

class ProjectService:
    def __init__(self, db: Session):
        self.repo = ProjectRepository(db)

    def create_project(self, user_id: int, payload: ProjectCreate):
        project = self.repo.create(user_id, payload.name, payload.description)
        return project

    def get_user_projects(self, user_id: int) -> List:
        return self.repo.get_by_user(user_id)

    def get_project(self, project_id: int, user_id: int):
        project = self.repo.get(project_id)
        if not project or user_id not in [u.id for u in project.users]:
            raise NotFoundError("Project not found or access denied")
        return project

    def update_project(self, project_id: int, user_id: int, payload: ProjectUpdate):
        project = self.get_project(project_id, user_id)
        if project.owner_id != user_id:
            raise PermissionDenied("Only owner can update project")
        return self.repo.update(project_id, payload.name, payload.description)

    def delete_project(self, project_id: int, user_id: int):
        project = self.get_project(project_id, user_id)
        if project.owner_id != user_id:
            raise PermissionDenied("Only owner can delete project")
        self.repo.delete(project_id)

    def invite_user(self, project_id: int, owner_id: int, login: str):
        project = self.get_project(project_id, owner_id)
        if project.owner_id != owner_id:
            raise PermissionDenied("Only owner can invite")
        self.repo.add_user_by_login(project_id, login)