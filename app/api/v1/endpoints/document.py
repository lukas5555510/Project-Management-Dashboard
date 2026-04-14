from io import BytesIO
from typing import List

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from starlette import status
from starlette.responses import StreamingResponse

from app.core.security import get_current_user_id
from app.schemas.document import DocumentResponse, DocumentUpdate
from app.services.document_service import DocumentService

router = APIRouter()

@router.get(
    "/project/{project_id}/documents",
    response_model=List[DocumentResponse],
    summary="Get project documents",
    description=(
        "Retrieves all documents associated with a specific project.\n\n"
        "This endpoint:\n"
        "- Verifies that the user has access to the project (owner or participant)\n"
        "- Fetches all related documents from the database\n"
        "- Returns a list of document metadata\n\n"
        "Authentication is required."
    ),
    responses={
        200: {"description": "Documents successfully retrieved"},
        401: {"description": "Unauthorized (user not authenticated)"},
        403: {"description": "Forbidden (no access to project)"},
        500: {"description": "Database error during retrieval"},
    },
)
def get_project_documents(
    project_id: int,
    user_id: int = Depends(get_current_user_id),
    document_service: DocumentService = Depends()
):
    return document_service.get_project_documents(project_id, user_id)

@router.post(
    "/project/{project_id}/documents",
    status_code = 201,
    response_model=DocumentResponse,
    summary="Upload document to project",
    description=(
        "Uploads a new document to a project.\n\n"
        "This endpoint:\n"
        "- Validates that the project exists\n"
        "- Ensures the user has access to the project\n"
        "- Uploads the file to storage (e.g., S3)\n"
        "- Stores document metadata in the database\n\n"
        "Requires multipart/form-data with a file field.\n\n"
        "Authentication is required."
    ),
    responses={
        201: {"description": "Document successfully uploaded"},
        401: {"description": "Unauthorized (user not authenticated)"},
        403: {"description": "Forbidden (no access to project)"},
        404: {"description": "Project not found"},
        500: {"description": "Database error during upload"},
    },
)
def upload_document(
    project_id: int,
    file: UploadFile = File(...),
    user_id: int = Depends(get_current_user_id),
    document_service: DocumentService = Depends()
):
    return document_service.upload_document(project_id, user_id, file)


@router.get(
    "/document/{document_id}",
    summary="Download document file",
    description=(
        "Downloads a document file by its ID.\n\n"
        "This endpoint:\n"
        "- Validates that the document exists\n"
        "- Ensures the user has access to the related project\n"
        "- Retrieves the file from storage\n"
        "- Returns the file as a streamed response with proper headers\n\n"
        "Authentication is required."
    ),
    responses={
        200: {"description": "File successfully downloaded"},
        401: {"description": "Unauthorized (user not authenticated)"},
        403: {"description": "Forbidden (no access to project)"},
        404: {"description": "Document not found"},
        500: {"description": "Error retrieving file or database issue"},
    },
)
def download_document(
    document_id: int,
    user_id: int = Depends(get_current_user_id),
    document_service: DocumentService = Depends()
):
    file_stream, filename, content_type = document_service.download_document(
        document_id=document_id,
        user_id=user_id
    )

    return StreamingResponse(
        file_stream,
        media_type=content_type,
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )

@router.put(
    "/document/{document_id}",
    response_model=DocumentResponse,
    summary="Update document",
    description=(
        "Replaces an existing document with a new file.\n\n"
        "This endpoint:\n"
        "- Validates that the document exists\n"
        "- Deletes the existing file from storage\n"
        "- Uploads a new file\n"
        "- Updates the document metadata in the database\n\n"
        "Requires multipart/form-data with a file field.\n\n"
        "Authentication is required."
    ),
    responses={
        200: {"description": "Document successfully updated"},
        401: {"description": "Unauthorized (user not authenticated)"},
        403: {"description": "User has no access"},
        404: {"description": "Document not found"},
        500: {"description": "Database or storage error during update"},
    },
)
def update_document(
    document_id: int,
    file: UploadFile = File(...),
    user_id: int = Depends(get_current_user_id),
    document_service: DocumentService = Depends()
):
    return document_service.update_document(user_id, document_id, file)


@router.delete(
    "/document/{document_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete document",
    description=(
        "Deletes a document from both storage and database.\n\n"
        "This endpoint:\n"
        "- Validates that the document exists\n"
        "- Ensures the user is the project owner\n"
        "- Deletes the file from storage (e.g., S3)\n"
        "- Removes the document record from the database\n\n"
        "This operation is restricted to project owners.\n\n"
        "Authentication is required."
    ),
    responses={
        200: {"description": "Document successfully deleted"},
        401: {"description": "Unauthorized (user not authenticated)"},
        403: {"description": "Forbidden (only owner can delete)"},
        404: {"description": "Document not found"},
        500: {"description": "Database or storage error during deletion"},
    },
)
def delete_document(
    document_id: int,
    user_id: int = Depends(get_current_user_id),
    document_service: DocumentService = Depends()
):

    if not document_service.delete_document(document_id,user_id):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete document"
        )

    return {"message": "Document deleted successfully"}