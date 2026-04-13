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
        Retrieve all projects accessible to a user.

        :param user_id: ID of the user whose projects are being retrieved
        :return: List of Project objects accessible to the user
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
        Retrieve a project by ID if accessible to the user.

        :param user_id: ID of the user requesting the project
        :param project_id: ID of the project to retrieve
        :return: Project object if found and accessible, otherwise None
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
        """
        Create a new project in the database.

        :param name: Name of the project
        :param description: Description of the project
        :return: The created Project object
        """

        obj = Project(name=name, description=description)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj


    def update_project(self, user_id: int, project_id: int, project: dict) -> Project | None:
        """
        Update a project in database.

        :param user_id: ID of the user requesting the update
        :param project_id: ID of the project to update
        :param project: Dictionary of fields to update
        :return: Updated Project object if found, otherwise None
        """

        obj = self.get_project_by_id(user_id,project_id)

        if not obj:
            return None

        for field, value in project.items():
            setattr(obj, field, value)

        self.db.commit()
        self.db.refresh(obj)

        return obj

    def delete_project(self, project_id: int) -> True | False:
        """
        Delete a project by ID.

        :param project_id: ID of the project to delete
        :return: True if the project was deleted, False if it was not found
        """

        obj = self.db.query(Project).filter(Project.id == project_id).first()
        if not obj:
            return False
        self.db.delete(obj)
        self.db.commit()

        return True


class ProjectUserRepository:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    def seed_roles(self) -> None:
        """
        Seed default roles into the database if they do not already exist.
        Ensures that all predefined roles from ROLES are present in the database.

        :return: None
        """
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
        """
        Assign 'owner' role to a user for a project.

        :param project_id: ID of the project
        :param user_id: ID of the user to assign as owner
        :return: Created ProjectUser association object
        """

        role = self.db.query(Role).filter(Role.name == "owner").one()
        obj = ProjectUser(user_id=user_id,project_id=project_id, role_id=role.id)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)

        return obj

    def create_access(self, project_id: int, user_id: int):
        """
        Grant 'participant' access to a user for a project.

        :param project_id: ID of the project
        :param user_id: ID of the user to grant access
        :return: Created ProjectUser association object
        """
        role = self.db.query(Role).filter(Role.name == "participant").one()
        obj = ProjectUser(user_id=user_id,project_id=project_id, role_id=role.id)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)

        return obj

    def is_user_owner(self, user_id: int, project_id: int) -> bool:
        """
        Check if a user is the owner of a project.

        :param user_id: ID of the user
        :param project_id: ID of the project
        :return: True if user is owner of the project, otherwise False
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
        Check if a user has access (owner or participant) to a project.

        :param user_id: ID of the user
        :param project_id: ID of the project
        :return: True if user has access to the project, otherwise False
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


