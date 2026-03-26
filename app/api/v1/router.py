from fastapi import APIRouter
from .endpoints import auth, project, document

router = APIRouter()

router.include_router(auth.router, prefix="/auth")
router.include_router(project.router, prefix="/project")
router.include_router(document.router, prefix="/document")