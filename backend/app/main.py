from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.database import engine
from app.db import models

from app.routers.auth import router as auth_router
from app.routers.users import router as users_router
from app.routers.emergency import router as emergency_router
from app.routers.ws_emergencies import router as ws_router

app = FastAPI(title="Rapid Maternal API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

models.Base.metadata.create_all(bind=engine)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(emergency_router, prefix="/emergencies", tags=["emergencies"])
app.include_router(ws_router)

@app.get("/")
def root():
    return {"message": "Rapid Maternal Backend is running"}
