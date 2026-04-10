from io import BytesIO
from typing import List

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from starlette import status
from starlette.responses import StreamingResponse

from app.core.security import get_current_user_id
from app.schemas.document import DocumentResponse, DocumentUpdate
from app.services.document_service import DocumentService

router = APIRouter()

@router.get("/project/{project_id}/documents", response_model = List[DocumentResponse])
def get_project_documents(
    project_id: int,
    user_id: int = Depends(get_current_user_id),
    document_service: DocumentService = Depends()
):
    """Get all documents for a specific project"""
    return document_service.get_project_documents(project_id, user_id)

@router.post("/project/{project_id}/documents", response_model = DocumentResponse)
def upload_document(
    project_id: int,
    file: UploadFile = File(...),
    user_id: int = Depends(get_current_user_id),
    document_service: DocumentService = Depends()
):
    """Upload a new document to a project"""
    # return DocumentResponse(id = 1, s3_path = "asdf",project_id = 2)
    return document_service.upload_document(project_id, file)


@router.get("/document/{document_id}")
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

@router.put("/document/{document_id}", response_model=DocumentResponse)
def update_document(
    document_id: int,
    file: UploadFile = File(...),
    user_id: int = Depends(get_current_user_id),
    document_service: DocumentService = Depends()
):
    """Update document metadata"""
    return document_service.update_document(document_id, file)


@router.delete("/document/{document_id}", status_code=status.HTTP_200_OK)
def delete_document(
    document_id: int,
    user_id: int = Depends(get_current_user_id),
    document_service: DocumentService = Depends()
):
    """Delete a document"""
    if not document_service.delete_document(document_id,user_id):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete document"
        )

    return {"message": "Document deleted successfully"}