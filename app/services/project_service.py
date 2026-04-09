from typing import List

from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.document_repository import DocumentRepository
from app.repositories.project_repository import ProjectRepository, ProjectUserRepository
from app.repositories.user_repository import UserRepository
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse
from app.core.exceptions import PermissionDenied, NotFoundError

class ProjectService:
    def __init__(self, db: Session = Depends(get_db)):
        self.project_repo = ProjectRepository(db)
        self.project_user_repo = ProjectUserRepository(db)
        self.user_repo = UserRepository(db)
        self.document_repo = DocumentRepository(db)

    def create_project(self, user_id: int, payload: ProjectCreate):
        project = self.project_repo.create_project(payload.name, payload.description)
        self.project_user_repo.create_ownership(project.id, user_id)
        return ProjectResponse(id=project.id,name=project.name,description=project.description)

    def get_user_projects(self, user_id: int) -> List:
        return self.project_repo.get_by_user(user_id)

    def get_projects_for_user(self, user_id: int):
        project_list = self.project_user_repo.get_all_project_available_for_user(user_id)

        result_list = []

        return result_list

    def update_project(self, project_id: int, user_id: int, payload: ProjectUpdate):
        project = self.get_project(project_id, user_id)
        if project.owner_id != user_id:
            raise PermissionDenied("Only owner can update project")
        return self.project_repo.update(project_id, payload.name, payload.description)

    def delete_project(self, project_id: int, user_id: int):
        project = self.get_project(project_id, user_id)
        if not self.project_user_repo.is_user_owner(project.id, user_id):
            raise PermissionDenied("Only owner can delete project")
        self.project_repo.delete_project(project_id)

    def grant_access_to_project(self, project_id: int, user_id: int, login: str):
        if not self.project_user_repo.is_user_owner(user_id, project_id):
            raise PermissionDenied("Only owner can invite")
        user_for_who_we_grant_access = self.user_repo.get_user_by_login(login)
        return self.project_user_repo.create_access(project_id,user_for_who_we_grant_access.id)
