import pytest
from unittest.mock import MagicMock, patch
from fastapi import UploadFile

from app.services.document_service import DocumentService
from app.core.exceptions import (
    NotFoundError,
    PermissionDenied,
    DatabaseRequestError,
)

@pytest.fixture
def service():
    service = DocumentService.__new__(DocumentService)

    service.repo = MagicMock()
    service.repo_project_user = MagicMock()
    service.repo_project = MagicMock()
    service.s3_client = MagicMock()

    return service

class TestDocumentService:
    def test_get_project_documents_permission_denied(self,service):
        service.repo_project_user.user_has_access.return_value = False

        with pytest.raises(PermissionDenied):
            service.get_project_documents(project_id=1, user_id=10)

        service.repo_project_user.user_has_access.assert_called_once_with(10, 1)


    def test_upload_document_project_not_found(self,service):
        service.repo_project.get_project_by_id.return_value = None

        file = MagicMock(spec=UploadFile)

        with pytest.raises(NotFoundError):
            service.upload_document(1, 10, file)


    def test_upload_document_permission_denied(self,service):
        service.repo_project.get_project_by_id.return_value = MagicMock()
        service.repo_project_user.user_has_access.return_value = False

        file = MagicMock(spec=UploadFile)

        with pytest.raises(PermissionDenied):
            service.upload_document(1, 10, file)


    def test_upload_document_success(self,service):
        service.repo_project.get_project_by_id.return_value = MagicMock()
        service.repo_project_user.user_has_access.return_value = True

        file = MagicMock(spec=UploadFile)
        file.filename = "test.pdf"

        created_doc = MagicMock()
        created_doc.s3_path = "documents/uuid_test.pdf"
        created_doc.project_id = 1

        service.repo.create_document.return_value = created_doc

        with patch("app.services.document_service.uuid.uuid4", return_value="uuid"), \
             patch("app.services.document_service.DocumentResponse.model_validate") as validate:

            validate.return_value = {"id": 1, "s3_path": created_doc.s3_path}

            result = service.upload_document(1, 10, file)

        service.s3_client.upload_file.assert_called_once()
        service.repo.create_document.assert_called_once()

        assert result["s3_path"] == created_doc.s3_path

    def test_download_document_not_found(self,service):
        service.repo.get_by_document_id.return_value = None

        with pytest.raises(NotFoundError):
            service.download_document(document_id=1, user_id=10)

    def test_download_document_permission_denied(self,service):
        doc = MagicMock()
        doc.project_id = 1
        doc.s3_path = "documents/4j6456jedje5_file.pdf"

        service.repo.get_by_document_id.return_value = doc
        service.repo_project_user.user_has_access.return_value = False

        with pytest.raises(PermissionDenied):
            service.download_document(1, 10)


    def test_download_document_success(self,service):
        doc = MagicMock()
        doc.project_id = 1
        doc.s3_path = "documents/4h56J5j6_file_test.pdf"

        service.repo.get_by_document_id.return_value = doc
        service.repo_project_user.user_has_access.return_value = True

        service.s3_client.download_file.return_value = {
            "Body": b"file-content",
            "ContentType": "application/pdf",
        }

        result = service.download_document(1, 10)

        body, filename, content_type = result

        assert body == b"file-content"
        assert content_type == "application/pdf"
        assert "file_test.pdf" in filename


    def test_update_document_not_found(self,service):
        service.repo.get_by_document_id.return_value = None

        file = MagicMock(spec=UploadFile)

        with pytest.raises(NotFoundError):
            service.update_document(1, file)


    def test_update_document_success(self,service):
        existing = MagicMock()
        existing.s3_path = "old/file.pdf"
        existing.project_id = 1

        service.repo.get_by_document_id.return_value = existing

        file = MagicMock(spec=UploadFile)
        file.filename = "new.pdf"

        updated = MagicMock()
        updated.s3_path = "documents/new_uuid_new.pdf"
        updated.project_id = 1

        service.repo.update_document.return_value = updated

        with patch("app.services.document_service.uuid.uuid4", return_value="new_uuid"), \
             patch("app.services.document_service.DocumentResponse.model_validate") as validate:

            validate.return_value = {"s3_path": updated.s3_path}

            result = service.update_document(1, file)

        service.repo.delete_document.assert_called_once()
        service.s3_client.upload_file.assert_called_once()
        assert result["s3_path"] == updated.s3_path


    def test_delete_document_not_found(self,service):
        service.repo.get_by_document_id.return_value = None

        with pytest.raises(NotFoundError):
            service.delete_document(1, 10)

    def test_delete_document_permission_denied(self,service):
        doc = MagicMock()
        doc.project_id = 1

        service.repo.get_by_document_id.return_value = doc
        service.repo_project_user.is_user_owner.return_value = False

        with pytest.raises(PermissionDenied):
            service.delete_document(1, 10)


    def test_delete_document_success(self,service):
        doc = MagicMock()
        doc.project_id = 1
        doc.s3_path = "documents/34h3h_file.pdf"

        service.repo.get_by_document_id.return_value = doc
        service.repo_project_user.is_user_owner.return_value = True
        service.repo.delete_document.return_value = {"success": True}

        result = service.delete_document(1, 10)

        service.s3_client.delete_file.assert_called_once_with("documents/34h3h_file.pdf")
        assert result == {"success": True}