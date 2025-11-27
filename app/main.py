from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core import settings
from app.api.v1 import diagnosis_router 

app = FastAPI(title=settings.PROJECT_NAME)

# CORS (Allow Frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(diagnosis_router, prefix="/api/v1", tags=["Diagnosis"])

@app.get("/")
def health_check():
    return {"status": "VunaGuide Brain Online", "version": "1.0.0"}