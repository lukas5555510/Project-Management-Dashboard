from fastapi import Depends
from sqlalchemy import or_, and_

from app.db.session import get_db
from app.models.project import Project, Role, ProjectUser
from app.models.user import User
from sqlalchemy.orm import Session, joinedload
from typing import List
from app.core.constants import ROLES



class ProjectRepository:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    def get_all_projects_for_user(self, user_id: int) -> List[Project]:
        """
        Get all projects accessible to a user with eager loading of documents.
        """
        return (
            self.db.query(Project)
            .options(joinedload(Project.documents))  # Eager load documents
            .join(ProjectUser, ProjectUser.project_id == Project.id)
            .join(Role, Role.id == ProjectUser.role_id)
            .filter(
                ProjectUser.user_id == user_id,
                Role.name.in_(["participant", "owner"])
            )
            .distinct()
            .all()
        )

    def get_project_by_id(self, user_id: int, project_id: int) -> Project:
        """
        Get project accessible to a user with eager loading of documents.
        """
        return (
            self.db.query(Project)
            .options(joinedload(Project.documents))  # Eager load documents
            .join(ProjectUser, ProjectUser.project_id == Project.id)
            .join(Role, Role.id == ProjectUser.role_id)
            .filter(
                ProjectUser.user_id == user_id,
                Role.name.in_(["participant", "owner"]),
                Project.id == project_id,
            )
            .distinct()
            .first()
        )

    def create_project(self, name: str, description: str) -> Project:
        obj = Project(name=name, description=description)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj


    def update_project(self, user_id: int, project_id: int, project: dict) -> Project | None:
        obj = self.get_project_by_id(user_id,project_id)

        if not obj:
            return None

        for field, value in project.items():
            setattr(obj, field, value)

        self.db.commit()
        self.db.refresh(obj)

        return obj

    def delete_project(self, project_id: int) -> True | False:
        obj = self.db.query(Project).filter(Project.id == project_id).first()
        if not obj:
            return False
        self.db.delete(obj)
        self.db.commit()

        return True


class ProjectUserRepository:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    def seed_roles(self):

        existing_roles = {
            role.name for role in self.db.query(Role).filter(Role.name.in_(ROLES)).all()
        }

        missing_roles = [
            Role(name =role_name)
            for role_name in ROLES
            if role_name not in existing_roles
        ]

        if missing_roles:
            self.db.add_all(missing_roles)
            self.db.commit()

    def create_ownership(self, project_id: int, user_id: int) -> ProjectUser:
        role = self.db.query(Role).filter(Role.name == "owner").one()
        obj = ProjectUser(user_id=user_id,project_id=project_id, role_id=role.id)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)

        return obj

    def create_access(self, project_id: int, user_id: int):
        role = self.db.query(Role).filter(Role.name == "participant").one()
        obj = ProjectUser(user_id=user_id,project_id=project_id, role_id=role.id)
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
        Returns True if the user is an 'owner/participant' of the project, False otherwise.
        """
        return (
                self.db.query(User)
                .join(ProjectUser, ProjectUser.user_id == User.id)
                .join(Role, Role.id == ProjectUser.role_id)
                .filter(
                    and_(
                        ProjectUser.project_id == project_id,
                        ProjectUser.user_id == user_id,
                        Role.name.in_(["participant", "owner"])
                    )
                )
                .count() > 0
        )


