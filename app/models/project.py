from sqlalchemy import Column, Integer, String, ForeignKey, Text, UniqueConstraint
from app.db.base import Base, relationship

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text)

    # relationships

    users = relationship(
        "ProjectUser",
        back_populates="project",
        cascade="all, delete-orphan"
    )

    documents = relationship(
        "Document",
        back_populates="project",
        cascade="all, delete-orphan"
    )


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)

    project_users = relationship(
        "ProjectUser",
        back_populates="role"
    )


class ProjectUser(Base):
    __tablename__ = "project_users"

    id = Column(Integer, primary_key=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)

    # relationships
    user = relationship("User", back_populates="projects")
    project = relationship("Project", back_populates="users")
    role = relationship("Role", back_populates="project_users")

    __table_args__ = (
        UniqueConstraint('user_id', 'project_id', 'role_id', name='uix_user_project_role'),
    )

