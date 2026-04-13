from fastapi import APIRouter
from .endpoints import auth, project, document

router = APIRouter()

router.include_router(auth.router, tags=["auth"])
router.include_router(project.router, tags=["project"])
router.include_router(document.router, tags=["document"])