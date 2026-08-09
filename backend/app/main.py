from fastapi import FastAPI
from app.api import health, auth, chat

app = FastAPI()

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(chat.router)

@app.get("/")
def read_root():
    return {"message": "AI Workspace Assistant backend is running!"}

# @app.get("/health")
# def read_root():
#     return {"status":"OK"}