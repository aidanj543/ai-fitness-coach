from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="AI Fitness Coach API",
    version = "0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["http://localhost:5173"],
    allow_credentials= False,
    allow_methods = ["GET"],
    allow_headers=["*"]
)

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "ai-fitness-coach-api"
    }

@app.get("/welcome")
def welcome():
    return {
        "message": "Welcome to the AI Fitness Coach API."
    }