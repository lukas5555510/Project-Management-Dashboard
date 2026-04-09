from app.repositories.project_repository import ProjectUserRepository
from app.db.session import SessionLocal

def seed_roles():
    db = SessionLocal()
    try:
        repo = ProjectUserRepository(db=db)
        repo.seed_roles()
    finally:
        db.close()