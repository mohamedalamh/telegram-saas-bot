from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"status": "running"}

@app.get("/users")
def users():
    return {"message": "dashboard working"}
