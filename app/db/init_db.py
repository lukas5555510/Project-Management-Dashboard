from app.db.base import Base
from app.db.session import engine
from app.models.project import Role, Project, ProjectUser
from app.models.user import User
from app.models.document import Document

def init_db():
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully")
    from app.db.seed import seed_roles
    seed_roles()
    print("Roles data seeded")


if __name__ == "__main__":
    init_db()

# while my_app will be containeraized through dockerfile
# there won't be need to provide more than db : password usernme
# and docker will connect it with db