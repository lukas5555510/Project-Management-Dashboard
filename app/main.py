from fastapi import FastAPI, Request
from starlette.responses import JSONResponse
from app.api.router import router as api_router
from app.core.exceptions import NotFoundError, PermissionDenied
from app.db.init_db import init_db

app = FastAPI(title="Project Management API")

app.include_router(api_router)


@app.exception_handler(NotFoundError)
async def not_found_handler(request: Request, exc: NotFoundError):
    return JSONResponse(status_code=404, content={"detail": "Resource not found"})


@app.exception_handler(PermissionDenied)
async def permission_handler(request: Request, exc: PermissionDenied):
    return JSONResponse(status_code=403, content={"detail": "Access denied"})


init_db()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app)