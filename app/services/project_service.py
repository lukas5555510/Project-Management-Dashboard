from typing import List

from fastapi import Depends
from pydantic import ValidationError
import logging
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.integrations.aws.s3_client import S3Client
from app.repositories.document_repository import DocumentRepository
from app.repositories.project_repository import ProjectRepository, ProjectUserRepository
from app.repositories.user_repository import UserRepository
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse
from app.core.exceptions import PermissionDenied, NotFoundError, ConflictException, DatabaseRequestError
from app.utils.serializers import serialize_project


logger = logging.getLogger(__name__)

class ProjectService:
    def __init__(self, db: Session = Depends(get_db)):
        self.project_repo = ProjectRepository(db)
        self.project_user_repo = ProjectUserRepository(db)
        self.user_repo = UserRepository(db)
        self.document_repo = DocumentRepository(db)
        self.s3_client = S3Client()


    def create_project(self, user_id: int, payload: ProjectCreate) -> ProjectResponse:
        """
        Create a new project and assign ownership to the creator.

        This method performs the full project creation workflow:
        - Creates a new project in the database
        - Assigns the requesting user as the project owner
        - Returns a serialized ProjectResponse with an empty documents list

        :param user_id: ID of the user creating the project
        :param payload: ProjectCreate schema containing project name and description
        :return: ProjectResponse representing the created project
        :raises DatabaseRequestError: If a database error occurs during creation
        """
        try:
            project = self.project_repo.create_project(payload.name, payload.description)
            self.project_user_repo.create_ownership(project.id, user_id)

            return ProjectResponse(
                id=project.id,name=project.name,
                description=project.description,
                documents=[]
            )
        except SQLAlchemyError:
            raise DatabaseRequestError("Database error creating project")



    def get_user_projects_with_documents(self, user_id: int) -> List[ProjectResponse]:
        """
        Retrieve all projects accessible to a user along with their documents.

        This method performs the following steps:
        - Fetches all projects where the user has access (owner or participant)
        - Iterates through each project and its related documents
        - Converts database models into response schemas (ProjectResponse, DocumentSchema)
        - Skips invalid project or document records with logging warnings

        :param user_id: ID of the user whose projects are being retrieved
        :return: List of ProjectResponse objects with nested document data
        :raises DatabaseRequestError: If a database error occurs during retrieval
        """
        try:
            # Getting projects with documents from repository
            projects = self.project_repo.get_all_projects_for_user(user_id)
            result = []

            for project in projects:
                try:
                    result.append(serialize_project(project))

                except ValidationError as proj_err:
                    logger.error(f"Project validation failed for project_id={project.id}: {proj_err}")
                    # Skip invalid project
                    continue

            return result

        except SQLAlchemyError:
            raise DatabaseRequestError("Database error getting projects")


    def get_project(self, user_id:int, project_id: int) -> ProjectResponse:
        """
        Retrieve a single project with its documents if the user has access.

        This method:
        - Retrieves the project by ID with access control
        - Validates that the project exists and is accessible to the user
        - Converts the project and its documents into response schemas
        - Skips invalid document records with logging warnings

        :param user_id: ID of the user requesting the project
        :param project_id: ID of the project to retrieve
        :return: ProjectResponse containing project data and documents
        :raises NotFoundError: If the project does not exist or is not accessible
        :raises DatabaseRequestError: If a database error occurs during retrieval
        """

        try:
            project = self.project_repo.get_project_by_id(user_id, project_id)
            return ProjectResponse.model_validate(serialize_project(project))

        except ValidationError:
            raise
        except SQLAlchemyError:
            raise DatabaseRequestError("Database error getting project")



    def update_project(self, project_id: int, user_id: int, project: ProjectUpdate) -> ProjectResponse:
        """
        Update an existing project with new data.

        This method:
        - Converts incoming update schema into a dictionary of changed fields
        - Applies updates to the project if the user has access
        - Validates that the project exists
        - Returns the updated project as a ProjectResponse

        :param project_id: ID of the project to update
        :param user_id: ID of the user requesting the update
        :param project: ProjectUpdate schema containing fields to modify
        :return: Updated ProjectResponse
        :raises PermissionDenied: If user has no access to the project
        :raises NotFoundError: If the project does not exist or is not accessible
        :raises DatabaseRequestError: If a database error occurs during update
        """

        try:
            if not self.project_repo.get_project_by_id(user_id, project_id):
                raise NotFoundError("Project not found")
            if not self.project_user_repo.user_has_access(user_id, project_id):
                raise PermissionDenied("User had no access to this project")
            project_dict = project.model_dump(exclude_unset=True)
            project = self.project_repo.update_project(user_id,project_id,project_dict)

            return ProjectResponse.model_validate(project)

        except SQLAlchemyError:
            raise DatabaseRequestError("Database error updating project")


    def delete_project(self, user_id: int, project_id: int):
        """
        Delete a project and its associated external resources.

        This method performs a full cleanup operation:
        - Verifies that the requesting user is the project owner
        - Ensures the project exists and is accessible
        - Retrieves all documents associated with the project
        - Deletes all related files from S3 storage
        - Deletes the project record from the database

        :param user_id: ID of the user requesting deletion
        :param project_id: ID of the project to delete
        :return: Result of the deletion operation (typically success flag or confirmation)
        :raises PermissionDenied: If the user is not the project owner
        :raises NotFoundError: If the project does not exist
        :raises DatabaseRequestError: If a database error occurs during deletion
        """

        try:
            if not self.project_repo.get_project_by_id(user_id, project_id):
                raise NotFoundError("Project not found")
            if not self.project_user_repo.is_user_owner(user_id, project_id):
                raise PermissionDenied("Only owner can delete project")

            documents = self.document_repo.get_by_project_id(project_id)

            for doc in documents:
                self.s3_client.delete_file(doc.s3_path)

            return self.project_repo.delete_project(project_id)

        except SQLAlchemyError:
            raise DatabaseRequestError("Database error deleting project")


    def grant_access_to_project(self, project_id: int, user_id: int, login: str):
        """
        Grant a user access to a project.

        This method performs an access control workflow:
        - Verifies that the requesting user is the project owner
        - Retrieves the target user by login
        - Ensures the target user exists
        - Checks that the user does not already have access
        - Grants participant-level access to the project

        :param project_id: ID of the project
        :param user_id: ID of the user granting access (must be owner)
        :param login: Login of the user to be granted access
        :return: ProjectUser access association object
        :raises PermissionDenied: If the requester is not the project owner
        :raises NotFoundError: If the target user does not exist
        :raises ConflictException: If the user already has access
        :raises DatabaseRequestError: If a database error occurs during the operation
        """

        try:
            if not self.project_user_repo.is_user_owner(user_id, project_id):
                raise PermissionDenied("Only owner can invite")

            user_for_who_we_grant_access = self.user_repo.get_user_by_login(login)
            if not user_for_who_we_grant_access:
                raise NotFoundError("User with such login does not exist")

            if self.project_user_repo.user_has_access(user_for_who_we_grant_access.id, project_id):
                raise ConflictException("User already has access to this project")

            return self.project_user_repo.create_access(project_id,user_for_who_we_grant_access.id)
        except SQLAlchemyError:
            raise DatabaseRequestError("Database error granting access to project")