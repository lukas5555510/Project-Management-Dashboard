from sqlalchemy import Column, Integer, String, ForeignKey
from app.db.base import Base, relationship


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    login = Column(String)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    projects_users = relationship("ProjectUser", back_populates="users")