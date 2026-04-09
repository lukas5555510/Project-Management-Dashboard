from fastapi import FastAPI
from app.api.router import router as api_router
from app.db.init_db import init_db

app = FastAPI(title="Project Management API")

app.include_router(api_router)



init_db()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app)