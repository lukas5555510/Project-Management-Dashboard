from typing import List
from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.repositories.document_repository import DocumentRepository
from app.integrations.aws.s3_client import S3Client #upload_file, download_file
from app.core.exceptions import NotFoundError, PermissionDenied

class DocumentService:
    def __init__(self, db: Session):
        self.repo = DocumentRepository(db)
        self.s3_client = S3Client()

    def get_project_documents(self, project_id: int, user_id: int):
        if not self.repo.has_access(project_id, user_id):
            raise PermissionDenied()
        return self.repo.list_by_project(project_id)

    def upload_documents(self, project_id: int, user_id: int, files: List[UploadFile]):
        if not self.repo.has_access(project_id, user_id):
            raise PermissionDenied()
        uploaded = []
        for file in files:
            key = self.s3_client.upload_file(file)
            uploaded.append(self.repo.create(project_id, file.filename, key))
        return uploaded

    def get_document(self, document_id: int, user_id: int):
        doc = self.repo.get(document_id)
        if not doc or not self.repo.has_access(doc.project_id, user_id):
            raise NotFoundError()
        return download_file_from_s3(doc.s3_key)

    def update_document(self, document_id: int, user_id: int, file: UploadFile):
        doc = self.repo.get(document_id)
        if not doc or not self.repo.has_access(doc.project_id, user_id):
            raise NotFoundError()
        new_key = upload_file_to_s3(file)
        return self.repo.update(document_id, file.filename, new_key)

    def delete_document(self, document_id: int, user_id: int):
        doc = self.repo.get(document_id)
        if not doc or not self.repo.has_access(doc.project_id, user_id):
            raise NotFoundError()
        self.repo.delete(document_id)