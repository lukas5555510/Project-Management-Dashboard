from pydantic import BaseModel, ConfigDict


class DocumentCreate(BaseModel):
    s3_path: str
    project_id: int

class DocumentResponse(BaseModel):
    id: int
    s3_path: str
    project_id: int

    model_config = ConfigDict(from_attributes=True)

class DocumentUpdate(BaseModel):
    s3_path: str
    project_id: int

