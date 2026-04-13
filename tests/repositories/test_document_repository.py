import pytest
from unittest.mock import MagicMock

from app.repositories.document_repository import DocumentRepository
from app.models.user import User
from app.models.project import ProjectUser, Project
from app.models.document import Document


@pytest.fixture
def mock_db():
    return MagicMock()


@pytest.fixture
def repo(mock_db):
    return DocumentRepository(db=mock_db)

class TestDocumentRepository:
    # -------------------------
    # GET BY PROJECT ID
    # -------------------------

    def test_get_by_project_id_returns_documents(self,repo, mock_db):
        project_id = 1
        expected_docs = [
            Document(id=1, s3_path="file1", project_id=project_id),
            Document(id=2, s3_path="file2", project_id=project_id),
        ]

        mock_db.query.return_value.filter.return_value.all.return_value = expected_docs

        result = repo.get_by_project_id(project_id)

        assert result == expected_docs
        mock_db.query.assert_called_once_with(Document)


    def test_get_by_project_id_empty(self,repo, mock_db):
        mock_db.query.return_value.filter.return_value.all.return_value = []

        result = repo.get_by_project_id(999)

        assert result == []


    # -------------------------
    # GET BY DOCUMENT ID
    # -------------------------

    def test_get_by_document_id_found(self,repo, mock_db):
        doc = Document(id=1, s3_path="file", project_id=1)

        mock_db.query.return_value.filter.return_value.first.return_value = doc

        result = repo.get_by_document_id(1)

        assert result == doc


    def test_get_by_document_id_not_found(self,repo, mock_db):
        mock_db.query.return_value.filter.return_value.first.return_value = None

        result = repo.get_by_document_id(999)

        assert result is None


    # -------------------------
    # CREATE DOCUMENT
    # -------------------------

    def test_create_document_success(self,repo, mock_db):
        data = {
            "s3_path": "s3://bucket/file.pdf",
            "project_id": 1,
        }

        result = repo.create_document(data)

        assert isinstance(result, Document)
        assert result.s3_path == data["s3_path"]
        assert result.project_id == data["project_id"]

        mock_db.add.assert_called_once_with(result)
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once_with(result)


    # -------------------------
    # UPDATE DOCUMENT
    # -------------------------

    def test_update_document_success(self,repo, mock_db):
        doc = Document(id=1, s3_path="old_path", project_id=1)

        repo.get_by_document_id = MagicMock(return_value=doc)

        update_data = {
            "s3_path": "new_path",
        }

        result = repo.update_document(1, update_data)

        assert result == doc
        assert doc.s3_path == "new_path"

        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once_with(doc)


    def test_update_document_multiple_fields(self,repo, mock_db):
        doc = Document(id=1, s3_path="old", project_id=1)
        repo.get_by_document_id = MagicMock(return_value=doc)

        update_data = {
            "s3_path": "updated",
            "project_id": 2,
        }

        result = repo.update_document(1, update_data)

        assert result.project_id == 2
        assert result.s3_path == "updated"


    def test_update_document_not_found(self,repo, mock_db):
        repo.get_by_document_id = MagicMock(return_value=None)

        result = repo.update_document(1, {"s3_path": "x"})

        assert result is None
        mock_db.commit.assert_not_called()
        mock_db.refresh.assert_not_called()


    # -------------------------
    # DELETE DOCUMENT
    # -------------------------

    def test_delete_document_success(self,repo, mock_db):
        doc = Document(id=1, s3_path="file", project_id=1)

        repo.get_by_document_id = MagicMock(return_value=doc)

        result = repo.delete_document(1)

        assert result == doc

        mock_db.delete.assert_called_once_with(doc)
        mock_db.commit.assert_called_once()


    def test_delete_document_not_found(self,repo, mock_db):
        repo.get_by_document_id = MagicMock(return_value=None)

        result = repo.delete_document(1)

        assert result is None

        mock_db.delete.assert_not_called()
        mock_db.commit.assert_not_called()