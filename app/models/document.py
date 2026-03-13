from sqlalchemy import Column, Integer, String, ForeignKey
from app.db.base import Base, relationship

class Document(Base):

    __tablename__ = 'documents'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    content = Column(String)

    project_id = Column(Integer, ForeignKey('projects.id'))
    projects = relationship("Project", back_populates="documents")