from fastapi import FastAPI
from app.routes.incidents import router as incidents_router

# Create the FastAPI application
app = FastAPI(
    title="CivicLens Dispatch",
    description="Multimodal emergency incident triage API",
    version="0.1.0",
)

# Register the incidents routes with the app
app.include_router(incidents_router)

# Root endpoint (health check)
@app.get("/")
def root():
    return {"message": "CivicLens Dispatch API is running"}