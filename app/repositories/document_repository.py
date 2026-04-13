from fastapi import Depends

from app.db.session import get_db
from app.models.document import Document
from sqlalchemy.orm import Session
from typing import List


class DocumentRepository:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    def get_by_project_id(self, project_id: int) -> List[Document]:
        """
        Retrieve all documents belonging to a specific project.

        :param project_id: ID of the project whose documents should be fetched
        :return: List of Document objects (empty list if none found)
        """

        return self.db.query(Document).filter(Document.project_id == project_id).all()

    def get_by_document_id(self, document_id: int) -> Document:
        """
        Retrieve a single document by its unique ID.

        :param document_id: Unique identifier of the document
        :return: Document object if found, otherwise None
        """
        return self.db.query(Document).filter(Document.id == document_id).first()

    def update_document(self, document_id: int, document_data : dict) -> Document | None:
        """
        Update an existing document with new field values.

        :param document_id: ID of the document to update
        :param document_data: Dictionary of fields to update with their new values
        :return: Updated Document object if found, otherwise None
        """
        obj = self.get_by_document_id(document_id)
        if not obj:
            return None

        for field, value in document_data.items():
            setattr(obj, field, value)

        self.db.commit()
        self.db.refresh(obj)

        return obj

    def delete_document(self, document_id: int) -> Document | None:
        """
        Delete a document from the database.

        :param document_id: ID of the document to delete
        :return: Deleted Document object if it existed, otherwise None
        """
        obj = self.get_by_document_id(document_id)
        if not obj:
            return None

        self.db.delete(obj)
        self.db.commit()

        return obj

    def create_document(self, document_data: dict) -> Document:
        """
        Create and persist a new document in the database.

        :param document_data: Dictionary containing document fields and values
        :return: The newly created Document object
        """
        obj = Document(**document_data)

        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)

        return obj

