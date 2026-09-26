
from fastapi import APIRouter


router = APIRouter()


@router.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "LegalEaseAI"
    }


@router.get("/api")
def api_info():
    return {
        "message": "LegalEaseAI API is running.",
        "version": "1.0.0"
    }


