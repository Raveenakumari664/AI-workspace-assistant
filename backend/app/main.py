from fastapi import FastAPI
from app.api import health, auth

app = FastAPI()

app.include_router(health.router)
app.include_router(auth.router)

@app.get("/")
def read_root():
    return {"message": "AI Workspace Assistant backend is running!"}

# @app.get("/health")
# def read_root():
#     return {"status":"OK"}