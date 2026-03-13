from sqlalchemy import Column, Integer, String, ForeignKey
from app.db.base import Base, relationship

class ProjectUser(Base):

    __tablename__ = 'project_users'
    id = Column(Integer, primary_key=True)

    project_id = Column(Integer, ForeignKey('projects.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    role_id = Column(Integer, ForeignKey('roles.id'))

    users = relationship('User', backref='projects_users')
    roles = relationship('Role', backref='projects_users')