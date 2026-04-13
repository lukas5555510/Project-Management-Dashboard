import pytest
from io import BytesIO
from unittest.mock import MagicMock

from fastapi.testclient import TestClient
from starlette.responses import StreamingResponse

from app.main import app
from app.services.document_service import DocumentService


# -------------------------
# FIXTURES
# -------------------------

@pytest.fixture
def mock_document_service():
    return MagicMock(spec=DocumentService)


@pytest.fixture
def client(mock_document_service):
    from app.core.security import get_current_user_id

    # override auth dependency
    app.dependency_overrides[get_current_user_id] = lambda: 1
    app.dependency_overrides[DocumentService] = lambda: mock_document_service

    return TestClient(app)

class TestDocumentEndpoints:
    # -------------------------
    # GET PROJECT DOCUMENTS
    # -------------------------

    def test_get_project_documents_success(self,client, mock_document_service):
        mock_document_service.get_project_documents.return_value = [
            {"id": 1, "s3_path": "file1", "project_id": 10},
            {"id": 2, "s3_path": "file2", "project_id": 10},
        ]

        response = client.get("/project/10/documents")

        assert response.status_code == 200
        assert len(response.json()) == 2

        mock_document_service.get_project_documents.assert_called_once_with(10, 1)


    # -------------------------
    # UPLOAD DOCUMENT
    # -------------------------

    def test_upload_document_success(self,client, mock_document_service):
        file_content = b"hello world"
        file = ("file.txt", BytesIO(file_content), "text/plain")

        mock_document_service.upload_document.return_value = {
            "id": 1,
            "s3_path": "s3/file.txt",
            "project_id": 10
        }

        response = client.post(
            "/project/10/documents",
            files={"file": file}
        )

        assert response.status_code == 201
        assert response.json()["s3_path"] == "s3/file.txt"

        mock_document_service.upload_document.assert_called_once()


    # -------------------------
    # DOWNLOAD DOCUMENT
    # -------------------------

    def test_download_document_success(self,client, mock_document_service):
        file_stream = BytesIO(b"file content")

        mock_document_service.download_document.return_value = (
            file_stream,
            "file.txt",
            "text/plain"
        )

        response = client.get("/document/1")

        assert response.status_code == 200
        assert response.headers["content-disposition"] == 'attachment; filename="file.txt"'
        assert response.content == b"file content"

        mock_document_service.download_document.assert_called_once_with(
            document_id=1,
            user_id=1
        )


    # -------------------------
    # UPDATE DOCUMENT
    # -------------------------

    def test_update_document_success(self,client, mock_document_service):
        file = ("updated.txt", BytesIO(b"new content"), "text/plain")

        mock_document_service.update_document.return_value = {
            "id": 1,
            "s3_path": "s3/updated.txt",
            "project_id": 10
        }

        response = client.put(
            "/document/1",
            files={"file": file}
        )

        assert response.status_code == 200
        assert response.json()["s3_path"] == "s3/updated.txt"

        mock_document_service.update_document.assert_called_once()


    # -------------------------
    # DELETE DOCUMENT
    # -------------------------

    def test_delete_document_success(self,client, mock_document_service):
        mock_document_service.delete_document.return_value = True

        response = client.delete("/document/1")

        assert response.status_code == 200
        assert response.json() == {
            "message": "Document deleted successfully"
        }

        mock_document_service.delete_document.assert_called_once_with(1, 1)


    def test_delete_document_failure(self,client, mock_document_service):
        mock_document_service.delete_document.return_value = False

        response = client.delete("/document/1")

        assert response.status_code == 500
        assert response.json()["detail"] == "Failed to delete document"