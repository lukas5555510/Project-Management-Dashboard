from app.core.exceptions import NotFoundError, PermissionDenied


class ValidateAccessAndExistence:

    def __init__(self, project_repo, project_user_repo):
        self.project_repo = project_repo
        self.project_user_repo = project_user_repo

    def validate_project_exist(self, user_id, project_id) -> None:
        """
        Throws NotFoundError if the project does not exist

        :param user_id:
        :param project_id:
        :return: None
        :raises NotFoundError: If the project does not exist or is not accessible
        """
        if not self.project_repo.get_project_by_id(user_id, project_id):
            raise NotFoundError("Project not found")

    def validate_user_has_access(self, user_id, project_id) -> None:
        """
        Throws PermissionDenied if the user has access to the project

        :param user_id:
        :param project_id:
        :return: None
        :throws PermissionDenied: If the user has no access to the project
        """
        if not self.project_user_repo.user_has_access(user_id, project_id):
            raise PermissionDenied("User had no access to this project")

    def validate_user_has_ownership(self, user_id, project_id) -> None:
        """
        Throws PermissionDenied if the user is not owner of the project

        :param user_id:
        :param project_id:
        :return: None
        :throws PermissionDenied: If the user has no access to the project
        """
        if not self.project_user_repo.is_user_owner(user_id, project_id):
            raise PermissionDenied("User is not owner of this project")