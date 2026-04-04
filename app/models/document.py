from sqlalchemy import Column, Integer, String, ForeignKey, LargeBinary
from app.db.base import Base, relationship

class Document(Base):

    __tablename__ = 'documents'

    id = Column(Integer, primary_key=True)
    #key is used as an indicator to external database where its stored
    key = Column(String, nullable=False)

    project_id = Column(Integer, ForeignKey('projects.id'))
    projects = relationship("Project", back_populates="documents")