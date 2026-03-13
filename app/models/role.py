from sqlalchemy import Column, Integer, String, ForeignKey
from app.db.base import Base, relationship


class Role(Base):
    __tablename__ = 'roles'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)

    project_users = relationship("ProjectUser", back_populates="roles")