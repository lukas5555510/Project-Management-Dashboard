from sqlalchemy import Column, Integer, String, ForeignKey, LargeBinary
from app.db.base import Base, relationship

class Document(Base):

    __tablename__ = 'documents'

    id = Column(Integer, primary_key=True, index=True)
    s3_path = Column(String, nullable=False)
    project_id = Column(Integer, ForeignKey('projects.id'))

    projects = relationship("Project", back_populates="documents")