from fastapi import APIRouter, Path
from typing import List
from app.schemas.document import (
    DocumentResponse, DocumentUpdate,
    DocumentDelete, ProjectDocumentListResponse,
    ProjectDocumentUpload
)

router = APIRouter()

@router.get("/project/{project_id}/documents", response_model=ProjectDocumentListResponse)
def list_project_documents(project_id: int):
    ...

@router.post("/project/{project_id}/documents", response_model=ProjectDocumentUpload)
def upload_document(project_id: int, doc: ProjectDocumentUpload):
    ...

@router.get("/document/{document_id}", response_model=DocumentResponse)
def get_document(document_id: int):
    ...

@router.put("/document/{document_id}", response_model=DocumentUpdate)
def update_document(document_id: int, doc: DocumentUpdate):
    ...

@router.delete("/document/{document_id}", response_model=DocumentDelete)
def delete_document(document_id: int):
    ...