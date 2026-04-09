from fastapi import Depends

from app.db.session import get_db
from app.models.document import Document
from sqlalchemy.orm import Session
from typing import List


class DocumentRepository:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db
    # lambda functions for AWS service
    # aws sandbox, in learning platform, we can use bucket s3 bucket file uploaded here and it should be logged "file was uploaded"

    def get_by_project_id(self, project_id: int) -> List[Document]:
        # return all documents that belongs to certain project
        return self.db.query(Document).filter(Document.project_id == project_id).all()

    def get_by_document_id(self, document_id: int) -> Document:
        # returns document with certain id
        return self.db.query(Document).filter(Document.id == document_id).first()


    def update_document(self, document_id: int, document_data : dict) -> Document | None:
        # updates document in database
        obj = self.get_by_document_id(document_id)
        if not obj:
            return None

        for field, value in document_data.items():
            setattr(obj, field, value)

        self.db.commit()
        self.db.refresh(obj)

        return obj

    def delete_document(self, document_id: int) -> Document | None:
        # deletes document from database
        obj = self.get_by_document_id(document_id)
        if not obj:
            return None

        self.db.delete(obj)
        self.db.commit()

        return obj

    def delete_all_project_documents(self, project_id: int) -> int:
        deleted_count = (
            self.db.query(Document).filter(Document.project_id == project_id).delete(synchronize_session=False)
        )
        self.db.commit()
        return deleted_count

    def upload_documents(self, documents: List[dict]) -> List[Document]:
        # adds list of records to database
        objects = [Document(**document) for document in documents]

        self.db.add_all(objects)
        self.db.commit()

        return objects

    def create_document(self, document_data: dict) -> Document:
        # adds one document to database
        obj = Document(**document_data)

        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)

        return obj

