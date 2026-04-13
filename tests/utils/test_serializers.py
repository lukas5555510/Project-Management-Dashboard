import pytest
from pydantic import ValidationError

from app.utils.serializers import serialize_document, serialize_project

class TestSerializer:
    def test_serialize_document_success(self):
        class Doc:
            id = 1
            s3_path = "s3://file.pdf"
            project_id = 10

        result = serialize_document(Doc)

        assert result.id == 1
        assert result.s3_path == "s3://file.pdf"
        assert result.project_id == 10

    def test_serialize_document_validation_error(self):
        class BrokenDoc:
            id = 1
            s3_path = None
            project_id = 10

        with pytest.raises(ValidationError):
            serialize_document(BrokenDoc)

    def test_serialize_project_success_with_documents(self):
        class Doc:
            id = 1
            s3_path = "s3://file1"
            project_id = 10

        class Project:
            id = 100
            name = "Test Project"
            description = "Desc"
            documents = [Doc()]

        result = serialize_project(Project)

        assert result.id == 100
        assert result.name == "Test Project"
        assert result.description == "Desc"
        assert len(result.documents) == 1
        assert result.documents[0].id == 1

    def test_serialize_project_empty_documents(self):
        class Project:
            id = 100
            name = "Test"
            description = None
            documents = None  # edge case

        result = serialize_project(Project)

        assert result.id == 100
        assert result.documents == []

    def test_serialize_project_nested_validation_error(self):
        class BrokenDoc:
            id = 1
            s3_path = None
            project_id = 10

        class Project:
            id = 100
            name = "Test"
            description = "Desc"
            documents = [BrokenDoc()]

        with pytest.raises(ValidationError):
            serialize_project(Project)

