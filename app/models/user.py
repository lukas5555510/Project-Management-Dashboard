from sqlalchemy import Column, Integer, String, ForeignKey
from app.db.base import Base, relationship


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    login = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    project_users = relationship("ProjectUser", back_populates="users")