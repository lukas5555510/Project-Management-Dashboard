from typing import List

from fastapi import Depends, HTTPException
from pydantic import ValidationError
import logging
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from starlette import status

from app.db.session import get_db
from app.integrations.aws.s3_client import S3Client
from app.repositories.document_repository import DocumentRepository
from app.repositories.project_repository import ProjectRepository, ProjectUserRepository
from app.repositories.user_repository import UserRepository
from app.schemas.document import DocumentSchema
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse
from app.core.exceptions import PermissionDenied, NotFoundError

logger = logging.getLogger(__name__)

class ProjectService:
    def __init__(self, db: Session = Depends(get_db)):
        self.project_repo = ProjectRepository(db)
        self.project_user_repo = ProjectUserRepository(db)
        self.user_repo = UserRepository(db)
        self.document_repo = DocumentRepository(db)
        self.s3_client = S3Client()

    def create_project(self, user_id: int, payload: ProjectCreate):
        project = self.project_repo.create_project(payload.name, payload.description)
        self.project_user_repo.create_ownership(project.id, user_id)
        return ProjectResponse(id=project.id,name=project.name,description=project.description, documents=[])
# TODO refactor repeatable component
    def get_user_projects_with_documents(self, user_id: int) -> List[ProjectResponse]:
        """
        Get all projects with their documents for a specific user.
        """
        try:
            # Getting projects with documents from repository
            projects = self.project_repo.get_all_projects_for_user(user_id)
            result = []

            for project in projects:
                try:
                    # Converting each project to a dictionary with basic attributes
                    project_dict = {
                        "id": project.id,
                        "name": project.name,
                        "description": project.description,
                        "documents": []  # Initialize empty documents list
                    }

                    # Converting each document and add to the project's documents list
                    for doc in project.documents:
                        try:
                            # Convert SQLAlchemy Document to DocumentSchema
                            doc_dict = {
                                "id": doc.id,
                                "s3_path": doc.s3_path,
                                "project_id": doc.project_id
                            }
                            document = DocumentSchema.model_validate(doc_dict)
                            project_dict["documents"].append(document)
                        except ValidationError as doc_err:
                            logger.warning(f"Document validation failed for doc_id={doc.id}: {doc_err}")
                            # Skip invalid document
                            continue

                    #Creating the final ProjectResponse from the prepared dictionary
                    project_response = ProjectResponse.model_validate(project_dict)
                    result.append(project_response)

                except ValidationError as proj_err:
                    logger.error(f"Project validation failed for project_id={project.id}: {proj_err}")
                    # Skip invalid project
                    continue

            return result

        except SQLAlchemyError as e:
            logger.exception(f"Database error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred while fetching projects"
            )

    def get_project(self, user_id:int, project_id: int) -> ProjectResponse:
        try:
            project = self.project_repo.get_project_by_id(user_id, project_id)

            if not project:
                raise NotFoundError()

            project_dict = {
                "id": project.id,
                "name": project.name,
                "description": project.description,
                "documents": []  # Initialize empty documents list
            }
            for doc in project.documents:
                try:
                    # Convert SQLAlchemy Document to DocumentSchema
                    doc_dict = {
                        "id": doc.id,
                        "s3_path": doc.s3_path,
                        "project_id": doc.project_id
                    }
                    document = DocumentSchema.model_validate(doc_dict)
                    project_dict["documents"].append(document)
                except ValidationError as doc_err:
                    logger.warning(f"Document validation failed for doc_id={doc.id}: {doc_err}")
                    # Skip invalid document
                    continue

            return ProjectResponse.model_validate(project_dict)

        except SQLAlchemyError as e:
            logger.exception(f"Database error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred while fetching projects"
            )

    def update_project(self, project_id: int, user_id: int, project: ProjectUpdate):
        try:
            project_dict = project.model_dump(exclude_unset=True)
            project = self.project_repo.update_project(user_id,project_id,project_dict)

            if not project:
                raise NotFoundError()

            project_dict = {
                "id": project.id,
                "name": project.name,
                "description": project.description,
                "documents": []  # Initialize empty documents list
            }
            for doc in project.documents:
                try:
                    # Convert SQLAlchemy Document to DocumentSchema
                    doc_dict = {
                        "id": doc.id,
                        "s3_path": doc.s3_path,
                        "project_id": doc.project_id
                    }
                    document = DocumentSchema.model_validate(doc_dict)
                    project_dict["documents"].append(document)
                except ValidationError as doc_err:
                    logger.warning(f"Document validation failed for doc_id={doc.id}: {doc_err}")
                    # Skip invalid document
                    continue


            return ProjectResponse.model_validate(project)

        except SQLAlchemyError as e:
            logger.exception(f"Database error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred while fetching projects"
            )

    def delete_project(self, user_id: int, project_id: int):
        try:
            if not self.project_user_repo.is_user_owner(user_id, project_id):
                raise PermissionDenied("Only owner can delete project")

            documents = self.document_repo.get_by_project_id(project_id)

            for doc in documents:
                self.s3_client.delete_file(doc.s3_path)

            result = self.project_repo.delete_project(project_id)
            if not result:
                raise NotFoundError()
            return result

        except SQLAlchemyError as e:
            logger.exception(f"Database error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred while fetching projects"
            )

    def grant_access_to_project(self, project_id: int, user_id: int, login: str):

        if not self.project_user_repo.is_user_owner(user_id, project_id):
            raise PermissionDenied("Only owner can invite")
        user_for_who_we_grant_access = self.user_repo.get_user_by_login(login)
        return self.project_user_repo.create_access(project_id,user_for_who_we_grant_access.id)
