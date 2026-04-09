from sqlalchemy import Column, Integer, String, ForeignKey, LargeBinary
from app.db.base import Base, relationship

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True)
    s3_path = Column(String, nullable=False)  # S3 key
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)

    # relationships
    project = relationship("Project", back_populates="documents")