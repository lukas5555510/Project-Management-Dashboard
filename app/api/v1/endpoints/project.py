from typing import List

from fastapi import APIRouter, Depends, HTTPException, Response

from app.core.security import get_current_user_id
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse, ProjectDeleteResponse, \
    InvitingToProjectResponse, InvitingToProjectRequest
from app.services.project_service import ProjectService

router = APIRouter()

@router.post(
    "/projects",
    response_model=ProjectResponse,
    status_code = 201,
    summary="Create a new project",
    description=(
        "Creates a new project and assigns the requesting user as its owner.\n\n"
        "This endpoint performs the following actions:\n"
        "- Creates a new project with the provided name and description\n"
        "- Assigns ownership of the project to the authenticated user\n"
        "- Returns the created project with an empty documents list\n\n"
        "The user must be authenticated to perform this operation."
    ),
    responses={
        201: {"description": "Project successfully created"},
        401: {"description": "Unauthorized (user not authenticated)"},
        500: {"description": "Database error during project creation"},
    },
)
def create_project(
        project: ProjectCreate,
        user_id: int = Depends(get_current_user_id),
        project_service: ProjectService = Depends()
):
    return project_service.create_project(user_id, project)


@router.get(
    "/projects",
    response_model=List[ProjectResponse],
    summary="Get all user projects with documents",
    description=(
        "Retrieves all projects accessible to the authenticated user, including their documents.\n\n"
        "This endpoint performs the following actions:\n"
        "- Fetches all projects where the user is an owner or participant\n"
        "- Includes associated documents for each project\n"
        "- Returns a structured list of projects with nested document data\n\n"
        "Invalid project or document records (if any) are skipped during processing.\n\n"
        "The user must be authenticated to access this endpoint."
    ),
    responses={
        200: {"description": "List of projects successfully retrieved"},
        401: {"description": "Unauthorized (user not authenticated)"},
        500: {"description": "Database error during project retrieval"},
    },
)
def get_projects(
        project_service: ProjectService = Depends(),
        user_id: int = Depends(get_current_user_id)
):
    return project_service.get_user_projects_with_documents(user_id)


@router.get(
    "/project/{project_id}/info",
    response_model=ProjectResponse,
    summary="Get project details with documents",
    description=(
        "Retrieves a single project along with its associated documents.\n\n"
        "This endpoint:\n"
        "- Validates that the project exists\n"
        "- Ensures the authenticated user has access (owner or participant)\n"
        "- Returns project details including nested document data\n\n"
        "Invalid documents (if any) are skipped during processing.\n\n"
        "Authentication is required."
    ),
    responses={
        200: {"description": "Project successfully retrieved"},
        401: {"description": "Unauthorized (user not authenticated)"},
        403: {"description": "Project not accessible"},
        404: {"description": "Project not found"},
        500: {"description": "Database error during retrieval"},
    },
)
def get_project_info(
        project_id: int,
        project_service: ProjectService = Depends(),
        user_id: int = Depends(get_current_user_id)
):
    return project_service.get_project(user_id, project_id)


@router.put(
    "/project/{project_id}/info",
    response_model=ProjectUpdate,
    summary="Update project information",
    description=(
        "Updates an existing project's data.\n\n"
        "This endpoint:\n"
        "- Applies partial updates to project fields\n"
        "- Requires the user to have access to the project\n"
        "- Returns the updated project data\n\n"
        "Only provided fields are updated (PATCH-like behavior).\n\n"
        "Authentication is required."
    ),
    responses={
        200: {"description": "Project successfully updated"},
        401: {"description": "Unauthorized (user not authenticated)"},
        403: {"description": "Project not accessible"},
        404: {"description": "Project not found"},
        500: {"description": "Database error during update"},
    },
)
def update_project_info(
        project_id: int,
        project: ProjectUpdate,
        project_service: ProjectService = Depends(),
        user_id: int = Depends(get_current_user_id)
):
    return project_service.update_project(project_id, user_id, project)


@router.delete(
    "/project/{project_id}",
    response_model=ProjectDeleteResponse,
    summary="Delete a project",
    description=(
        "Deletes a project and all its associated resources.\n\n"
        "This endpoint:\n"
        "- Verifies that the user is the project owner\n"
        "- Deletes all related documents from storage (e.g., S3)\n"
        "- Removes the project from the database\n\n"
        "This operation is irreversible and restricted to project owners only.\n\n"
        "Authentication is required."
    ),
    responses={
        200: {"description": "Project successfully deleted"},
        401: {"description": "Unauthorized (user not authenticated)"},
        403: {"description": "Forbidden (user is not the project owner)"},
        404: {"description": "Project not found"},
        500: {"description": "Database error during deletion"},
    },
)
def delete_project(
        project_id: int,
        project_service: ProjectService = Depends(),
        user_id: int = Depends(get_current_user_id)
):

    return {
        "success": project_service.delete_project(user_id, project_id),
        "message": "Project deleted successfully",
        "deleted_id": project_id
    }


@router.post(
    "/project/{project_id}/invite",
    response_model=InvitingToProjectResponse,
    summary="Grant user access to a project",
    description=(
        "Grants a user access to a project by their login.\n\n"
        "This endpoint:\n"
        "- Verifies that the requester is the project owner\n"
        "- Finds the target user by login\n"
        "- Ensures the user does not already have access\n"
        "- Grants participant-level access to the project\n\n"
        "Only project owners can invite users.\n\n"
        "Authentication is required."
    ),
    responses={
        200: {"description": "Access successfully granted"},
        401: {"description": "Unauthorized (user not authenticated)"},
        403: {"description": "Forbidden (only owner can invite users)"},
        404: {"description": "User or project not found"},
        409: {"description": "User already has access to the project"},
        500: {"description": "Database error during operation"},
    },
)
def invite_user_to_project(
    project_id: int,
    login: InvitingToProjectRequest,
    user_id: int = Depends(get_current_user_id),
    project_service: ProjectService = Depends()
):

    project_service.grant_access_to_project(project_id, user_id, login.login)

    return {
        "message": "Access granted",
        "project_id": project_id,
        "login": login.login
    }