from sqlalchemy import or_, and_
from app.models.project import Project, Role, ProjectUser
from app.models.user import User
from sqlalchemy.orm import Session
from typing import List


class ProjectRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_project(self, user_id: int, name: str, description: str) -> Project:
        obj = Project(user_id=user_id, name=name, description=description)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

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

    def delete_project(self, project_id: int) -> Project | None:
        obj = self.get_by_project_id(project_id)
        if not obj:
            return None
        self.db.delete(obj)
        self.db.commit()

        return obj


class ProjectUserRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_ownership(self, project_id: int, user_id: int) -> ProjectUser:
        role = self.db.query(Role).filter(Role.name == "owner").one()
        obj = ProjectUser(project_id, user_id, role.id)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)

        return obj

    def create_access(self, project_id: int, user_id: int):
        role = self.db.query(Role).filter(Role.name == "access").one()
        obj = ProjectUser(project_id, user_id, role.id)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)

        return obj

    def is_user_owner(self, user_id: int, project_id: int) -> bool:
        """
        Returns True if the user is an 'owner' of the project, False otherwise.
        """
        return (
                self.db.query(User)
                .join(ProjectUser, ProjectUser.user_id == User.id)
                .join(Role, Role.id == ProjectUser.role_id)
                .filter(
                    and_(
                        ProjectUser.project_id == project_id,
                        ProjectUser.user_id == user_id,
                        Role.name == "owner"
                    )
                )
                .count() > 0
        )

    def user_has_access(self, user_id: int, project_id: int) -> bool:
        """
        Returns True if the user is an 'owner' of the project, False otherwise.
        """
        return (
                self.db.query(User)
                .join(ProjectUser, ProjectUser.user_id == User.id)
                .join(Role, Role.id == ProjectUser.role_id)
                .filter(
                    and_(
                        ProjectUser.project_id == project_id,
                        ProjectUser.user_id == user_id,
                        Role.name.in_(["access", "owner"])
                    )
                )
                .count() > 0
        )

    def get_all_project_available_for_user(self, user_id: int) -> List[Project]:
        return (
            self.db.query(Project)
            .join(ProjectUser, ProjectUser.project_id == Project.id)
            .join(Role, Role.id == ProjectUser.role_id)
            .filter(
                ProjectUser.user_id == user_id,
                Role.name.in_(["access", "owner"])
            )
            .distinct()
            .all()
        )

