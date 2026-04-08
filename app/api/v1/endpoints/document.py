from io import BytesIO
from typing import List

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from starlette import status
from starlette.responses import StreamingResponse

from app.api.deps import get_current_user_id
from app.schemas.document import DocumentResponse, DocumentUpdate
from app.services.document_service import DocumentService

router = APIRouter()

@router.get("/project/{project_id}/documents", response_model=List[DocumentResponse])
def get_project_documents(
    project_id: int,
    user_id: int = Depends(get_current_user_id),
    document_service: DocumentService = Depends()
):
    """Get all documents for a specific project"""
    return document_service.get_project_documents(project_id, user_id)


@router.post("/project/{project_id}/documents", response_model=DocumentResponse)
def upload_document(
    project_id: int,
    file: UploadFile = File(...),
    user_id: int = Depends(get_current_user_id),
    document_service: DocumentService = Depends()
):
    """Upload a new document to a project"""
    return document_service.upload_document(project_id, file)


@router.get("/document/{document_id}")
def download_document(
    document_id: int,
    user_id: int = Depends(get_current_user_id),
    document_service: DocumentService = Depends()
):
    """Download a specific document"""
    file_data = document_service.download_document(document_id)

    # Create a BytesIO object from the file content
    content_stream = BytesIO(file_data["content"])

    return StreamingResponse(
        content_stream,
        media_type=file_data["media_type"],
        headers={"Content-Disposition": f"attachment; filename={file_data['filename']}"}
    )


@router.put("/document/{document_id}", response_model=DocumentResponse)
def update_document(
    document_id: int,
    document_data: DocumentUpdate,
    user_id: int = Depends(get_current_user_id),
    document_service: DocumentService = Depends()
):
    """Update document metadata"""
    return document_service.update_document(document_id, document_data)


@router.delete("/document/{document_id}", status_code=status.HTTP_200_OK)
def delete_document(
    document_id: int,
    user_id: int = Depends(get_current_user_id),
    document_service: DocumentService = Depends()
):
    """Delete a document"""
    return document_service.delete_document(document_id)