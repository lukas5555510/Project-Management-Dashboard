import pytest
from unittest.mock import MagicMock, patch
from pydantic import ValidationError

from app.services.project_service import ProjectService
from app.core.exceptions import (
    NotFoundError,
    PermissionDenied,
    ConflictException,
    DatabaseRequestError,
)
from app.schemas.project import ProjectCreate, ProjectUpdate


@pytest.fixture
def service():
    service = ProjectService.__new__(ProjectService)

    service.project_repo = MagicMock()
    service.project_user_repo = MagicMock()
    service.user_repo = MagicMock()
    service.document_repo = MagicMock()
    service.s3_client = MagicMock()

    return service

class TestProjectService:
    def test_create_project_success(self,service):
        payload = ProjectCreate(name="Test", description="Desc")

        project = MagicMock()
        project.id = 1
        project.name = "Test"
        project.description = "Desc"

        service.project_repo.create_project.return_value = project

        result = service.create_project(user_id=10, payload=payload)

        service.project_repo.create_project.assert_called_once_with("Test", "Desc")
        service.project_user_repo.create_ownership.assert_called_once_with(1, 10)

        assert result.id == 1
        assert result.name == "Test"


    def test_create_project_db_error(self,service):
        service.project_repo.create_project.side_effect = DatabaseRequestError()

        payload = ProjectCreate(name="Test", description="Desc")

        with pytest.raises(DatabaseRequestError):
            service.create_project(10, payload)


    def test_get_user_projects_success(self,service):
        fake_projects = [MagicMock(id=1), MagicMock(id=2)]

        service.project_repo.get_all_projects_for_user.return_value = fake_projects

        with patch("app.services.project_service.serialize_project") as serialize:
            serialize.side_effect = lambda x: {
                "id": x.id,
                "name": "P",
                "documents": []
            }

            result = service.get_user_projects_with_documents(10)

        assert len(result) == 2
        service.project_repo.get_all_projects_for_user.assert_called_once_with(10)

    def test_get_user_projects_skip_invalid(self, service):
        fake_projects = [MagicMock(id=1), MagicMock(id=2)]
        service.project_repo.get_all_projects_for_user.return_value = fake_projects

        with patch("app.services.project_service.serialize_project") as serialize:
            serialize.side_effect = [
                ValidationError.from_exception_data(
                    "ProjectResponse",
                    [
                        {
                            "type": "missing",
                            "loc": ("name",),
                            "msg": "Field required",
                            "input": None,
                        }
                    ],
                ),
                {"id": 2},
            ]

            result = service.get_user_projects_with_documents(10)

        assert len(result) == 1

    def test_get_project_success(self,service):
        project = MagicMock()

        service.project_repo.get_project_by_id.return_value = project

        with patch("app.services.project_service.serialize_project", return_value={"id": 1}), \
             patch("app.schemas.project.ProjectResponse.model_validate") as validate:

            validate.return_value = {"id": 1}

            result = service.get_project(10, 1)

        assert result == {"id": 1}


    def test_get_project_db_error(self,service):
        service.project_repo.get_project_by_id.side_effect = DatabaseRequestError()

        with pytest.raises(DatabaseRequestError):
            service.get_project(10, 1)

    def test_update_project_success(self,service):
        service.project_repo.get_project_by_id.return_value = MagicMock()
        service.project_user_repo.user_has_access.return_value = True

        payload = ProjectUpdate(name="New", description="NewDesc")

        updated = MagicMock()
        updated.id = 1

        service.project_repo.update_project.return_value = updated

        with patch("app.schemas.project.ProjectResponse.model_validate") as validate:
            validate.return_value = {"id": 1}

            result = service.update_project(1, 10, payload)

        assert result == {"id": 1}
        service.project_repo.update_project.assert_called_once()


    def test_update_project_not_found(self,service):
        service.project_repo.get_project_by_id.return_value = None

        payload = ProjectUpdate(name="X", description="Y")

        with pytest.raises(NotFoundError):
            service.update_project(1, 10, payload)



    def test_update_project_permission_denied(self,service):
        service.project_repo.get_project_by_id.return_value = MagicMock()
        service.project_user_repo.user_has_access.return_value = False

        payload = ProjectUpdate(name="X", description="Y")

        with pytest.raises(PermissionDenied):
            service.update_project(1, 10, payload)

    def test_delete_project_success(self,service):
        service.project_repo.get_project_by_id.return_value = MagicMock()
        service.project_user_repo.is_user_owner.return_value = True

        service.document_repo.get_by_project_id.return_value = [
            MagicMock(s3_path="file1"),
            MagicMock(s3_path="file2"),
        ]

        service.project_repo.delete_project.return_value = {"deleted": True}

        result = service.delete_project(10, 1)

        assert result == {"deleted": True}
        assert service.s3_client.delete_file.call_count == 2


    def test_grant_access_not_owner(self,service):
        service.project_user_repo.is_user_owner.return_value = False

        with pytest.raises(PermissionDenied):
            service.grant_access_to_project(1, 10, "john")


    def test_grant_access_user_not_found(self,service):
        service.project_user_repo.is_user_owner.return_value = True
        service.user_repo.get_user_by_login.return_value = None

        with pytest.raises(NotFoundError):
            service.grant_access_to_project(1, 10, "john")


    def test_grant_access_conflict(self,service):
        service.project_user_repo.is_user_owner.return_value = True

        user = MagicMock()
        user.id = 5

        service.user_repo.get_user_by_login.return_value = user
        service.project_user_repo.user_has_access.return_value = True

        with pytest.raises(ConflictException):
            service.grant_access_to_project(1, 10, "john")


    def test_grant_access_success(self,service):
        service.project_user_repo.is_user_owner.return_value = True

        user = MagicMock()
        user.id = 5

        service.user_repo.get_user_by_login.return_value = user
        service.project_user_repo.user_has_access.return_value = False
        service.project_user_repo.create_access.return_value = {"ok": True}

        result = service.grant_access_to_project(1, 10, "john")

        assert result == {"ok": True}


