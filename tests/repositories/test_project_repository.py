import pytest
from unittest.mock import MagicMock

from app.repositories.project_repository import ProjectRepository, ProjectUserRepository
from app.models.user import User
from app.models.project import ProjectUser, Project, Role
from app.models.document import Document

ROLES = ["owner", "participant"]

@pytest.fixture
def mock_db():
    return MagicMock()


@pytest.fixture
def repo(mock_db):
    return ProjectRepository(db=mock_db)

class TestProjectRepository:
    # -------------------------
    # GET ALL PROJECTS FOR USER
    # -------------------------

    def test_get_all_projects_for_user_returns_projects(self,repo, mock_db):
        user_id = 1

        projects = [
            Project(id=1, name="Project 1", description="desc"),
            Project(id=2, name="Project 2", description="desc"),
        ]

        # mock chain
        mock_query = mock_db.query.return_value
        mock_query.options.return_value = mock_query
        mock_query.join.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.distinct.return_value = mock_query
        mock_query.all.return_value = projects

        result = repo.get_all_projects_for_user(user_id)

        assert result == projects
        mock_db.query.assert_called_once_with(Project)
        assert mock_query.join.call_count == 2  # ProjectUser + Role


    def test_get_all_projects_for_user_empty(self,repo, mock_db):
        mock_query = mock_db.query.return_value
        mock_query.options.return_value = mock_query
        mock_query.join.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.distinct.return_value = mock_query
        mock_query.all.return_value = []

        result = repo.get_all_projects_for_user(999)

        assert result == []


    # -------------------------
    # GET PROJECT BY ID
    # -------------------------

    def test_get_project_by_id_found(self,repo, mock_db):
        project = Project(id=1, name="Test", description="desc")

        mock_query = mock_db.query.return_value
        mock_query.options.return_value = mock_query
        mock_query.join.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.distinct.return_value = mock_query
        mock_query.first.return_value = project

        result = repo.get_project_by_id(user_id=1, project_id=1)

        assert result == project


    def test_get_project_by_id_not_found(self,repo, mock_db):
        mock_query = mock_db.query.return_value
        mock_query.options.return_value = mock_query
        mock_query.join.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.distinct.return_value = mock_query
        mock_query.first.return_value = None

        result = repo.get_project_by_id(user_id=1, project_id=999)

        assert result is None


    # -------------------------
    # CREATE PROJECT
    # -------------------------

    def test_create_project_success(self,repo, mock_db):
        name = "New Project"
        description = "desc"

        result = repo.create_project(name, description)

        assert isinstance(result, Project)
        assert result.name == name
        assert result.description == description

        mock_db.add.assert_called_once_with(result)
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once_with(result)


    # -------------------------
    # UPDATE PROJECT
    # -------------------------

    def test_update_project_success(self,repo, mock_db):
        project = Project(id=1, name="Old", description="Old desc")

        repo.get_project_by_id = MagicMock(return_value=project)

        update_data = {
            "name": "Updated",
            "description": "Updated desc",
        }

        result = repo.update_project(user_id=1, project_id=1, project=update_data)

        assert result == project
        assert project.name == "Updated"
        assert project.description == "Updated desc"

        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once_with(project)


    def test_update_project_not_found(self,repo, mock_db):
        repo.get_project_by_id = MagicMock(return_value=None)

        result = repo.update_project(1, 1, {"name": "X"})

        assert result is None
        mock_db.commit.assert_not_called()


    # -------------------------
    # DELETE PROJECT
    # -------------------------

    def test_delete_project_success(self,repo, mock_db):
        project = Project(id=1, name="Test", description="desc")

        mock_db.query.return_value.filter.return_value.first.return_value = project

        result = repo.delete_project(1)

        assert result is True
        mock_db.delete.assert_called_once_with(project)
        mock_db.commit.assert_called_once()


    def test_delete_project_not_found(self,repo, mock_db):
        mock_db.query.return_value.filter.return_value.first.return_value = None

        result = repo.delete_project(999)

        assert result is False
        mock_db.delete.assert_not_called()
        mock_db.commit.assert_not_called()





@pytest.fixture
def repo_project_user(mock_db):
    return ProjectUserRepository(db=mock_db)

class TestProjectUserRepository:
    # -------------------------
    # SEED ROLES
    # -------------------------

    def test_seed_roles_adds_missing_roles(self,repo_project_user, mock_db):
        # assume only one role exists in DB
        existing_role = Role(name=ROLES[0])

        mock_db.query.return_value.filter.return_value.all.return_value = [existing_role]

        repo_project_user.seed_roles()

        # should add remaining roles
        added_roles = mock_db.add_all.call_args[0][0]

        assert len(added_roles) == len(ROLES) - 1
        assert all(isinstance(r, Role) for r in added_roles)

        mock_db.add_all.assert_called_once()
        mock_db.commit.assert_called_once()


    def test_seed_roles_no_missing(self,repo_project_user, mock_db):
        existing_roles = [Role(name=role) for role in ROLES]

        mock_db.query.return_value.filter.return_value.all.return_value = existing_roles

        repo_project_user.seed_roles()

        mock_db.add_all.assert_not_called()
        mock_db.commit.assert_not_called()


    # -------------------------
    # CREATE OWNERSHIP
    # -------------------------

    def test_create_ownership_success(self,repo_project_user, mock_db):
        role = Role(id=1, name="owner")

        mock_db.query.return_value.filter.return_value.one.return_value = role

        result = repo_project_user.create_ownership(project_id=1, user_id=2)

        assert isinstance(result, ProjectUser)
        assert result.project_id == 1
        assert result.user_id == 2
        assert result.role_id == role.id

        mock_db.add.assert_called_once_with(result)
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once_with(result)


    # -------------------------
    # CREATE ACCESS
    # -------------------------

    def test_create_access_success(self,repo_project_user, mock_db):
        role = Role(id=2, name="participant")

        mock_db.query.return_value.filter.return_value.one.return_value = role

        result = repo_project_user.create_access(project_id=1, user_id=3)

        assert isinstance(result, ProjectUser)
        assert result.project_id == 1
        assert result.user_id == 3
        assert result.role_id == role.id

        mock_db.add.assert_called_once_with(result)
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once_with(result)


    # -------------------------
    # IS USER OWNER
    # -------------------------

    def test_is_user_owner_true(self,repo_project_user, mock_db):
        mock_db.query.return_value.join.return_value.join.return_value.filter.return_value.count.return_value = 1

        result = repo_project_user.is_user_owner(user_id=1, project_id=1)

        assert result is True


    def test_is_user_owner_false(self,repo_project_user, mock_db):
        mock_db.query.return_value.join.return_value.join.return_value.filter.return_value.count.return_value = 0

        result = repo_project_user.is_user_owner(user_id=1, project_id=1)

        assert result is False


    # -------------------------
    # USER HAS ACCESS
    # -------------------------

    def test_user_has_access_true(self,repo_project_user, mock_db):
        mock_db.query.return_value.join.return_value.join.return_value.filter.return_value.count.return_value = 2

        result = repo_project_user.user_has_access(user_id=1, project_id=1)

        assert result is True


    def test_user_has_access_false(self,repo_project_user, mock_db):
        mock_db.query.return_value.join.return_value.join.return_value.filter.return_value.count.return_value = 0

        result = repo_project_user.user_has_access(user_id=1, project_id=1)

        assert result is False

