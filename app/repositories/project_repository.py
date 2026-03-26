from app.models.project import Project, Role, ProjectUser
from sqlalchemy.orm import Session
from typing import List


class ProjectRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_project_id(self, project_id: int) -> Project:
        return self.db.query(Project).filter(Project.project_id == project_id).one()

    def update_project(self, project_id: int, project: dict) -> Project | None:
        obj = self.get_by_project_id(project_id)

        if not obj:
            return None

        for field, value in project.items():
            setattr(obj, field, value)

        self.db.commit()
        self.db.refresh(obj)

        return obj

    def get_projects_for_user(self, user_id: int):
        return (
            self.db.query(Project)
            .join(ProjectUser, Project.id == ProjectUser.project_id)
            .filter(ProjectUser.user_id == user_id)
            .all()
        )
