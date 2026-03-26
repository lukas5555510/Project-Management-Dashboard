from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# GET /document/<document_id>
class DocumentResponse(BaseModel):
    id: int
    project_id: int
    filename: str
    content: bytes
    uploaded_at: datetime

# PUT /document/<document_id>
class DocumentUpdate(BaseModel):
    filename: Optional[str] = None
    content: Optional[str] = None

# DELETE /document/<document_id>
class DocumentDelete(BaseModel):
    message: str

class UploadingList(BaseModel):
    items: list[DocumentResponse] = []

# GET /project/<project_id>/documents
class ProjectDocumentListResponse(UploadingList):
    pass

# POST /project/<project_id>/documents
class ProjectDocumentUpload(UploadingList):
    pass