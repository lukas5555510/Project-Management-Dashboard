from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from app.schemas.document import DocumentUpdate
from app.services.document_service import DocumentService

router = APIRouter()

@router.get("/project/{project_id}/documents")
async def get_documents(project_id: int, document_service: DocumentService = Depends()):
    return await document_service.get_documents(project_id)

@router.post("/project/{project_id}/documents")
async def upload_document(project_id: int, file: UploadFile = File(...), document_service: DocumentService = Depends()):
    return await document_service.upload_document(project_id, file)

@router.get("/document/{document_id}")
async def download_document(document_id: int, document_service: DocumentService = Depends()):
    return await document_service.download_document(document_id)

@router.put("/document/{document_id}", response_model=DocumentUpdate)
async def update_document(document_id: int, document: DocumentUpdate, document_service: DocumentService = Depends()):
    return await document_service.update_document(document_id, document)

@router.delete("/document/{document_id}")
async def delete_document(document_id: int, document_service: DocumentService = Depends()):
    return await document_service.delete_document(document_id)