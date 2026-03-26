from sqlalchemy import Column, Integer, String, ForeignKey, LargeBinary
from app.db.base import Base, relationship

class Document(Base):

    __tablename__ = 'documents'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    filetype = Column(String, nullable=False)
    content = Column(String, nullable=False)
    #it will be a path so the documents will be stored in AWS

    project_id = Column(Integer, ForeignKey('projects.id'))
    projects = relationship("Project", back_populates="documents")