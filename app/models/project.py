from sqlalchemy import Column, Integer, String, ForeignKey
from app.db.base import Base, relationship

class Project(Base):

    __tablename__ = 'projects'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    documents = relationship("Document", back_populates="projects")

class ProjectUser(Base):

    __tablename__ = 'project_users'
    id = Column(Integer, primary_key=True)

    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    role_id = Column(Integer, ForeignKey('roles.id'), nullable=False)
    users = relationship('User', backref='project_users')
    roles = relationship('Role', backref='project_users')

class Role(Base):
    __tablename__ = 'roles'
    # example roles, owner / access
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)

    project_users = relationship("ProjectUser", back_populates="roles")