from fastapi import APIRouter
from .endpoints import auth, project, document

router = APIRouter()

router.include_router(auth.router, tags=["Auth"])
router.include_router(project.router, tags=["Project"])
router.include_router(document.router, tags=["Document"])