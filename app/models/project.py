from sqlalchemy import Column, Integer, String, ForeignKey
from app.db.base import Base, relationship

class Project(Base):

    __tablename__ = 'projects'

    id = Column(Integer, promary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)

    documents = relationship("Document", back_populates="projects")
