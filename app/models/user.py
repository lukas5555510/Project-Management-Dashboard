from sqlalchemy import Column, Integer, String, ForeignKey
from app.db.base import Base, relationship


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    login = Column(String, nullable=False, unique=True)
    email = Column(String, nullable=False, unique=True)
    hashed_password = Column(String, nullable=False)

    # relationships
    projects = relationship(
        "ProjectUser",
        back_populates="user",
        cascade="all, delete-orphan"
    )
