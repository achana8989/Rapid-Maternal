from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.database import engine
from app.db import models   # 🔥 THIS IMPORT IS CRITICAL

app = FastAPI(title="Rapid Maternal API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ CREATE TABLES
models.Base.metadata.create_all(bind=engine)

from app.api import emergencies
app.include_router(emergencies.router)

@app.get("/")
def root():
    return {"message": "Rapid Maternal Backend is running"}

