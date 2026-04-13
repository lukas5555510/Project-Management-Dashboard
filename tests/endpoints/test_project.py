import pytest
from unittest.mock import MagicMock

from botocore.exceptions import ClientError
from fastapi.testclient import TestClient

from app.core.exceptions import NotFoundError, PermissionDenied, ConflictException
from app.integrations.aws.s3_client import S3Client
from app.main import app
from app.services.project_service import ProjectService
from app.core.security import get_current_user_id


# -------------------------
# FIXTURES
# -------------------------

@pytest.fixture
def mock_project_service():
    return MagicMock(spec=ProjectService)


@pytest.fixture
def client(mock_project_service):
    app.dependency_overrides[get_current_user_id] = lambda: 1
    app.dependency_overrides[ProjectService] = lambda: mock_project_service

    return TestClient(app)

class TestProjectEndpoints:
    # -------------------------
    # CREATE PROJECT
    # -------------------------

    def test_create_project(self,client, mock_project_service):
        payload = {
            "name": "Test Project",
            "description": "desc"
        }

        mock_project_service.create_project.return_value = {
            "id": 1,
            "name": "Test Project",
            "description": "desc",
            "documents": []
        }

        response = client.post("/projects", json=payload)

        assert response.status_code == 201
        assert response.json()["name"] == "Test Project"
        assert response.json()["documents"] == []

        mock_project_service.create_project.assert_called_once()

        args, _ = mock_project_service.create_project.call_args
        assert args[0] == 1  # user_id
        assert args[1].name == "Test Project"

    def test_create_project_unauthorized(self,client,mock_project_service):
        app.dependency_overrides.clear()

        response = client.post("/projects", json={
            "name": "Test project",
            "description": "desc"
        })

        assert response.status_code == 401

    def test_create_project_invalid_payload(self,client, mock_project_service):
        response = client.post("/projects", json={
            "nam": "asd"  # invalid  name
        })

        assert response.status_code == 422

    # -------------------------
    # GET ALL PROJECTS
    # -------------------------

    def test_get_projects(self,client, mock_project_service):
        mock_project_service.get_user_projects_with_documents.return_value = [
            {"id": 1, "name": "A", "documents": []}
        ]

        response = client.get("/projects")

        assert response.status_code == 200
        assert isinstance(response.json(), list)

        mock_project_service.get_user_projects_with_documents.assert_called_once_with(1)

    def test_get_projects_empty_list(self,client, mock_project_service):
        mock_project_service.get_user_projects_with_documents.return_value = []

        response = client.get("/projects")

        assert response.status_code == 200
        assert response.json() == []

    def test_get_projects_unauthorized(self,client):
        app.dependency_overrides.clear()

        response = client.get("/projects")

        assert response.status_code == 401


    # -------------------------
    # GET PROJECT INFO
    # -------------------------

    def test_get_project_info(self,client, mock_project_service):
        mock_project_service.get_project.return_value = {
            "id": 1,
            "name": "Project",
            "documents": []
        }

        response = client.get("/project/1/info")

        assert response.status_code == 200
        assert response.json()["id"] == 1

        mock_project_service.get_project.assert_called_once_with(1, 1)

    def test_get_project_not_found(self, client, mock_project_service):
        mock_project_service.get_project.side_effect = NotFoundError("Not Found")

        response = client.get("/project/999/info")

        # depends on your exception handler; commonly:
        assert response.status_code == 404

    def test_get_project_forbidden_access(self,client, mock_project_service):
        mock_project_service.get_project.side_effect = PermissionDenied()

        response = client.get("/project/1/info")

        assert response.status_code == 403


    # -------------------------
    # UPDATE PROJECT
    # -------------------------

    def test_update_project(self,client, mock_project_service):
        payload = {
            "name": "Updated",
            "description": "Updated desc"
        }

        mock_project_service.update_project.return_value = {
            "name": "Updated",
            "description": "Updated desc"
        }

        response = client.put("/project/1/info", json=payload)

        assert response.status_code == 200
        assert response.json()["name"] == "Updated"

        mock_project_service.update_project.assert_called_once()

        args, _ = mock_project_service.update_project.call_args
        assert args[0] == 1  # project_id
        assert args[1] == 1  # user_id
        assert args[2].name == "Updated"

    def test_update_project_invalid_payload(self, client, mock_project_service):
        response = client.put("/project/1/info", json={
            "nam": ""  # invalid
        })

        assert response.status_code == 422

    def test_update_project_not_found(self, client, mock_project_service):
        mock_project_service.update_project.side_effect = NotFoundError("Not Found")

        response = client.put("/project/1/info", json={
            "name": "new name",
            "description": "desc"
        })

        assert response.status_code == 404

    def test_update_project_forbidden(self, client, mock_project_service):
        mock_project_service.update_project.side_effect = PermissionDenied()

        response = client.put("/project/1/info", json={
            "name": "new name",
            "description": "desc"
        })

        assert response.status_code == 403

    # -------------------------
    # DELETE PROJECT
    # -------------------------

    def test_delete_project(self,client, mock_project_service):
        mock_project_service.delete_project.return_value = True

        response = client.delete("/project/1")

        assert response.status_code == 200
        assert response.json() == {
            "success": True,
            "message": "Project deleted successfully",
            "deleted_id": 1
        }

        mock_project_service.delete_project.assert_called_once_with(1, 1)

    def test_delete_project_not_owner(self,client, mock_project_service):
        mock_project_service.delete_project.side_effect = PermissionDenied()

        response = client.delete("/project/1")

        assert response.status_code == 403

    def test_delete_project_not_found(self,client, mock_project_service):
        mock_project_service.delete_project.side_effect = NotFoundError("Not Found")

        response = client.delete("/project/999")

        assert response.status_code == 404

    def test_delete_project_partial_failure(self,client, mock_project_service):
        mock_project_service.delete_project.side_effect = ClientError(operation_name="Delete",error_response={"error":"yes"})

        response = client.delete("/project/1")

        assert response.status_code == 500

    # -------------------------
    # INVITE USER
    # -------------------------

    def test_invite_user(self,client, mock_project_service):
        payload = {
            "login": "john"
        }

        response = client.post("/project/1/invite", json=payload)

        assert response.status_code == 200
        assert response.json()["message"] == "Access granted"

        mock_project_service.grant_access_to_project.assert_called_once_with(
            1, 1, "john"
        )

    def test_invite_user_not_found(self,client, mock_project_service):
        mock_project_service.grant_access_to_project.side_effect = NotFoundError("User not found")

        response = client.post("/project/1/invite", json={
            "login": "unknown_user"
        })

        assert response.status_code == 404

    def test_invite_user_already_has_access(self,client, mock_project_service):
        mock_project_service.grant_access_to_project.side_effect = ConflictException("Already has access")

        response = client.post("/project/1/invite", json={
            "login": "existing_user"
        })

        assert response.status_code == 409

    def test_invite_user_forbidden(self,client, mock_project_service):
        mock_project_service.grant_access_to_project.side_effect = PermissionDenied("Forbidden")

        response = client.post("/project/1/invite", json={
            "login": "user"
        })

        assert response.status_code == 403