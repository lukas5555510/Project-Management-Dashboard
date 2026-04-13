from botocore.exceptions import ClientError
from fastapi import FastAPI, Request, HTTPException
from starlette.responses import JSONResponse
from app.api.router import router as api_router
from app.core.exceptions import NotFoundError, PermissionDenied, ConflictException, InvalidCredentialsError, \
    ConflictException, DatabaseRequestError
from app.db.init_db import init_db

def create_app():
    app = FastAPI(title="Project Management API")
    return app

app = create_app()


app.include_router(api_router)


@app.exception_handler(NotFoundError)
async def not_found_handler(request: Request, exc: NotFoundError):
    return JSONResponse(status_code=404, content={"description": f"{exc}"})

@app.exception_handler(InvalidCredentialsError)
async def invalid_credentials_handler(request: Request, exc: InvalidCredentialsError):
    return JSONResponse(status_code=401, content={"description": f"{exc}"})

@app.exception_handler(PermissionDenied)
async def permission_handler(request: Request, exc: PermissionDenied):
    return JSONResponse(status_code=403, content={"description": f"{exc}"})

@app.exception_handler(ConflictException)
async def user_already_invited(request: Request, exc: ConflictException):
    return JSONResponse(status_code=409, content={"description": f"{exc}"})

@app.exception_handler(ClientError)
async def client_error_handler(request: Request, exc: ClientError):
    return JSONResponse(status_code=500, content={"description": "S3 Error"})

# @app.exception_handler(HTTPException)
# async def http_exception_handler(request: Request, exc: HTTPException):
#     return JSONResponse(
#         status_code=exc.status_code,
#         content={
#             "error": True,
#             "status_code": exc.status_code,
#             "message": exc.detail,
#         },
#     )

@app.exception_handler(DatabaseRequestError)
async def database_exception_handler(request: Request, exc: DatabaseRequestError):
    return JSONResponse(status_code=500, content={"description": f"{exc}"})

@app.on_event("startup")
def startup():
    init_db()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app)