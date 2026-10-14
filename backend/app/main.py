from fastapi import FastAPI

app = FastAPI(
    title="AI Fitness Coach API",
    version = "0.1.0"
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