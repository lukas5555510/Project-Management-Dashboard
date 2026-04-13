from venv import logger

from pydantic import ValidationError

from app.schemas.document import DocumentSchema
from app.schemas.project import ProjectResponse


def serialize_document(doc) -> DocumentSchema:
    """
    Convert SQLAlchemy Document model to DocumentSchema.
    """
    try:
        doc_dict = {
            "id": doc.id,
            "s3_path": doc.s3_path,
            "project_id": doc.project_id
        }
        return DocumentSchema.model_validate(doc_dict)

    except ValidationError as e:
        logger.warning(
            "Document serialization failed",
            extra={"doc_id": getattr(doc, "id", None), "error": str(e)}
        )
        raise


def serialize_project(project) -> ProjectResponse:
    """
    Convert SQLAlchemy Project model to ProjectResponse,
    including nested documents.
    """
    try:
        project_dict = {
            "id": project.id,
            "name": project.name,
            "description": project.description,
            "documents": []
        }

        for doc in getattr(project, "documents", []) or []:
            serialized_doc = serialize_document(doc)
            if serialized_doc:
                project_dict["documents"].append(serialized_doc)

        return ProjectResponse.model_validate(project_dict)

    except ValidationError as e:
        logger.error(
            "Project serialization failed",
            extra={"project_id": getattr(project, "id", None), "error": str(e)}
        )
        raise