from fastapi import FastAPI
from app.core.config import settings
from app.db.database import engine
from app.db import models

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="RapidMaternal API",
    description="Real-time maternal emergency response system",
    version="0.1.0",
    debug=settings.app_debug
)


@app.get("/")
def health_check():
    return {
        "status": "ok",
        "environment": settings.app_env
    }
