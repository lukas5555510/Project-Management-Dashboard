import uuid
from typing import List, Dict, Any
from fastapi import UploadFile
from sqlalchemy.orm import Session
from starlette import status
from starlette.exceptions import HTTPException

from app.core.security import get_user_id_from_token
from app.models.document import Document
from app.repositories.document_repository import DocumentRepository
from app.integrations.aws.s3_client import S3Client #upload_file, download_file
from app.core.exceptions import NotFoundError, PermissionDenied
from app.repositories.project_repository import ProjectUserRepository
from app.schemas.document import DocumentResponse, DocumentUpdate


class DocumentService:
    def __init__(self, db: Session):
        self.repo = DocumentRepository(db)
        self.repo_project_user = ProjectUserRepository(db)
        self.s3_client = S3Client()

    def get_project_documents(self, project_id: int, user_id: int) -> List[DocumentResponse]:
        #Get documents from database
        if not self.repo_project_user.user_has_access(project_id, user_id):
            raise PermissionDenied()
        documents = self.repo.get_by_project_id(project_id)
        return [DocumentResponse.model_validate(doc) for doc in documents]

    def upload_document(self, project_id: int, file: UploadFile) -> DocumentResponse:
        # Generate a unique filename to avoid collisions in S3
        filename = f"{uuid.uuid4()}_{file.filename}"

        # Read file content
        file_content = file.file.read()

        # Upload the file to S3
        s3_path = f"projects/{project_id}/documents/{filename}"
        self.s3_client.upload_file(file_content, s3_path)

        # Create document record in database
        document_data = {
            "s3_path": s3_path,
            "project_id": project_id,
        }

        document = self.repo.create_document(document_data)
        return DocumentResponse.model_validate(document)

# to refactor
    def download_document(self, document_id: int) -> Dict[str, Any]:
        # Get document from database
        document = self.repo.get_by_document_id(document_id)
        if not document:
            raise NotFoundError(f"Document with id {document_id} not found")

        # Download file from S3
        file_content = self.s3_client.download_file(document.s3_path)

        # Return file for download
        return {
            "content": file_content,
        }

    def update_document(self, document_id: int, document_data: DocumentUpdate) -> DocumentResponse:
        # Get existing document
        existing_document = self.repo.get_by_document_id(document_id)
        if not existing_document:
            raise NotFoundError(f"Document with id {document_id} not found")

        # Update document
        updated_document = self.repo.update_document(
            document_id,
            document_data.model_dump(exclude_unset=True)
        )

        if not updated_document:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update document"
            )

        return DocumentResponse.model_validate(updated_document)

    def delete_document(self, document_id: int) -> dict:
        # Get document
        document = self.repo.get_by_document_id(document_id)
        if not document:
            raise NotFoundError(f"Document with id {document_id} not found")

        # Delete from S3 first
        try:
            self.s3_client.delete_file(document.s3_path)
        except Exception as e:
            # Log the error but continue with database deletion
            print(f"Error deleting file from S3: {e}")

        # Delete from database
        deleted_document = self.repo.delete_document(document_id)
        if not deleted_document:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete document"
            )

        return {"message": "Document deleted successfully"}