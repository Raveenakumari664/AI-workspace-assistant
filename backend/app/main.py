from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "AI Workspace Assistant backend is running!"}

@app.get("/health")
def read_root():
    return {"status":"OK"}