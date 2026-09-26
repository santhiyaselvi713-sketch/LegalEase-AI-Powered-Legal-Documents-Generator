from fastapi import FastAPI

from fastapi.middleware.cors import (
    CORSMiddleware
)

from backend.config import get_settings

from backend.routes import router


settings = get_settings()


app = FastAPI(

    title=settings.app_name,

    description=(
        "AI-powered legal document "
        "drafting API"
    ),

    version="1.0.0"
)


app.add_middleware(

    CORSMiddleware,

    allow_origins=["*"],

    allow_credentials=False,

    allow_methods=["*"],

    allow_headers=["*"]
)


app.include_router(router)


@app.get("/")
def root():

    return {

        "service":
            settings.app_name,

        "message":
            "LegalEase backend is running.",

        "docs":
            "/docs",

        "health":
            "/health"
    }