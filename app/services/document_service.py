import uuid
from typing import List, Dict, Any
from fastapi import UploadFile, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.repositories.document_repository import DocumentRepository
from app.integrations.aws.s3_client import S3Client
from app.core.exceptions import NotFoundError, PermissionDenied
from app.repositories.project_repository import ProjectUserRepository
from app.schemas.document import DocumentResponse


class DocumentService:
    def __init__(self, db: Session = Depends(get_db)):
        self.repo = DocumentRepository(db)
        self.repo_project_user = ProjectUserRepository(db)
        self.s3_client = S3Client()

    def get_project_documents(self, project_id: int, user_id: int) -> List[DocumentResponse]:
        #Get documents from database
        if not self.repo_project_user.user_has_access(user_id, project_id):
            raise PermissionDenied()
        documents = self.repo.get_by_project_id(project_id)
        return [DocumentResponse.model_validate(doc) for doc in documents]

    def upload_document(self, project_id: int, file: UploadFile) -> DocumentResponse:
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


    def download_document(self, document_id: int, user_id: int):
        # 1. Fetch metadata from DB
        document = self.repo.get_by_document_id(document_id)

        if not document:
            raise FileNotFoundError(f"{document_id} not found")

        # 2. Authorization check
        if not self.repo_project_user.user_has_access(user_id, document.project_id):
            raise PermissionDenied()

        # 3. Download file from S3
        file_stream = self.s3_client.download_file(document.s3_path)

        return file_stream['Body'], document.s3_path.split("_",1)[-1], file_stream['ContentType']



    def update_document(self, document_id: int, file: UploadFile) -> DocumentResponse:
        # Get existing document
        existing_document = self.repo.get_by_document_id(document_id)
        if not existing_document:
            raise NotFoundError(f"Document with id {document_id} not found")

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

    def delete_document(self, document_id: int,user_id:int) -> dict:
        # Get document
        document = self.repo.get_by_document_id(document_id)
        if not self.repo_project_user.is_user_owner(user_id,document.project_id):
            raise PermissionDenied("Only project owner can delete document")
        if not document:
            raise NotFoundError(f"Document with id {document_id} not found")

        # Delete from S3 first
        try:
            self.s3_client.delete_file(document.s3_path)
        except Exception as e:
            # Log the error but continue with database deletion
            print(f"Error deleting file from S3: {e}")

        # Delete from database
        return self.repo.delete_document(document_id)
