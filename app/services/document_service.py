import uuid
from typing import List
from fastapi import UploadFile, Depends
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.repositories.document_repository import DocumentRepository
from app.integrations.aws.s3_client import S3Client
from app.core.exceptions import NotFoundError, PermissionDenied, DatabaseRequestError
from app.repositories.project_repository import ProjectUserRepository, ProjectRepository
from app.schemas.document import DocumentResponse


class DocumentService:
    def __init__(self, db: Session = Depends(get_db)):
        self.repo = DocumentRepository(db)
        self.repo_project_user = ProjectUserRepository(db)
        self.repo_project = ProjectRepository(db)
        self.s3_client = S3Client()

    def get_project_documents(self, project_id: int, user_id: int) -> List[DocumentResponse]:
        """
        Retrieve all documents belonging to a project for an authorized user.

        This method performs the following steps:
        - Verifies that the user has access to the project
        - Fetches all documents associated with the given project from the database
        - Converts database models into response schemas (DocumentResponse)

        :param project_id: ID of the project whose documents are being retrieved
        :param user_id: ID of the user requesting the documents
        :return: List of DocumentResponse objects representing project documents
        :raises PermissionDenied: If the user does not have access to the project
        :raises DatabaseRequestError: If a database error occurs during retrieval
        """

        try:
            if not self.repo_project.get_project_by_id(user_id,project_id):
                raise NotFoundError("Project not found")
            if not self.repo_project_user.user_has_access(user_id, project_id):
                raise PermissionDenied("User has no access to project")
            documents = self.repo.get_by_project_id(project_id)
            return [DocumentResponse.model_validate(doc) for doc in documents]
        except SQLAlchemyError:
            raise DatabaseRequestError("Database error uploading/creating document")

    def upload_document(self, project_id: int,user_id: int, file: UploadFile) -> DocumentResponse:
        """
        Upload a new document to a project and persist its metadata.

        This method performs a full upload workflow:
        - Validates that the project exists
        - Checks that the user has access to the project
        - Generates a unique filename to avoid S3 key collisions
        - Uploads the file to S3 storage
        - Creates a corresponding document record in the database

        :param project_id: ID of the project to upload the document into
        :param user_id: ID of the user performing the upload
        :param file: Uploaded file object
        :return: DocumentResponse representing the created document
        :raises NotFoundError: If the project does not exist
        :raises PermissionDenied: If the user has no access to the project
        :raises DatabaseRequestError: If a database error occurs during creation
        """

        try:
            if not self.repo_project.get_project_by_id(user_id,project_id):
                raise NotFoundError("Project not found")
            if not self.repo_project_user.user_has_access(user_id, project_id):
                raise PermissionDenied("User has no access to project")

            # Generate a unique filename to avoid collisions in S3
            filename = f"{uuid.uuid4()}_{file.filename}"

            # Upload the file to S3
            s3_path = f"documents/{filename}"
            self.s3_client.upload_file(file, s3_path)

            # Create document record in database
            document_data = {
                "s3_path": s3_path,
                "project_id": project_id,
            }

            document = self.repo.create_document(document_data)
            return DocumentResponse.model_validate(document)

        except SQLAlchemyError:
            raise DatabaseRequestError("Database error uploading/creating document")


    def download_document(self, document_id: int, user_id: int):
        """
        Download a document file from storage if the user is authorized.

        This method performs the following steps:
        - Retrieves document metadata from the database
        - Validates that the document exists
        - Checks that the user has access to the associated project
        - Downloads the file from S3 storage
        - Returns the file stream along with filename and content type

        This is a read operation combining database lookup and external storage access.

        :param document_id: ID of the document to download
        :param user_id: ID of the user requesting the file
        :return: Tuple containing (file stream, original filename, content type)
        :raises NotFoundError: If the document does not exist
        :raises PermissionDenied: If the user has no access to the project
        :raises DatabaseRequestError: If a database error occurs during retrieval
        """

        try:
            document = self.repo.get_by_document_id(document_id)

            if not document:
                raise NotFoundError(f"Document not found")

            # 2. Authorization check
            if not self.repo_project_user.user_has_access(user_id, document.project_id):
                raise PermissionDenied("User has no access to project")

            # 3. Download file from S3
            file_stream = self.s3_client.download_file(document.s3_path)

            return file_stream['Body'], document.s3_path.split("_",1)[-1], file_stream['ContentType']
        except SQLAlchemyError:
            raise DatabaseRequestError("Database error download document")


    def update_document(self, document_id: int, file: UploadFile) -> DocumentResponse:
        """
        Replace an existing document with a new uploaded file.

        This method performs the following steps:
        - Retrieves the existing document record from the database
        - Validates that the document exists
        - Removes the old file from S3 storage
        - Uploads the new file to S3 with a unique filename
        - Updates the database record with the new file path

        :param document_id: ID of the document to update
        :param file: New file to replace the existing document
        :return: DocumentResponse representing the updated document
        :raises NotFoundError: If the document does not exist
        :raises DatabaseRequestError: If a database error occurs during update
        """

        try:
            existing_document = self.repo.get_by_document_id(document_id)
            if not existing_document:
                raise NotFoundError(f"Document with id {document_id} not found")

            # Delete old files from S3
            self.s3_client.delete_file_and_zip(existing_document.s3_path)

            filename = f"{uuid.uuid4()}_{file.filename}"
            # Upload the file to S3
            s3_path = f"documents/{filename}"
            self.s3_client.upload_file(file, s3_path)

            # Create document record in database
            document_data = {
                "s3_path": s3_path,
                "project_id": existing_document.project_id,
            }

            updated_document = self.repo.update_document(document_id, document_data)

            return DocumentResponse.model_validate(updated_document)

        except SQLAlchemyError:
            raise DatabaseRequestError("Database error updating document")


    def delete_document(self, document_id: int,user_id:int) -> dict:
        """
        Delete a document from both storage and database.

        This method performs the following steps:
        - Retrieves the document metadata from the database
        - Validates that the document exists
        - Ensures that the requesting user is the project owner
        - Deletes the file from S3 storage
        - Removes the document record from the database

        This is a destructive operation restricted to project owners only.

        :param document_id: ID of the document to delete
        :param user_id: ID of the user requesting deletion
        :return: Result of the deletion operation (typically success confirmation)
        :raises NotFoundError: If the document does not exist
        :raises PermissionDenied: If the user is not the project owner
        :raises DatabaseRequestError: If a database error occurs during deletion
        """

        try:
            document = self.repo.get_by_document_id(document_id)
            if not document:
                raise NotFoundError(f"Document not found")

            if not self.repo_project_user.is_user_owner(user_id,document.project_id):
                raise PermissionDenied("Only project owner can delete document")

            # Delete from S3 first
            self.s3_client.delete_file_and_zip(document.s3_path)

            return self.repo.delete_document(document_id)

        except SQLAlchemyError:
            raise DatabaseRequestError("Database error deleting document")


