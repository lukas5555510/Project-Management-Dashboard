import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient

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