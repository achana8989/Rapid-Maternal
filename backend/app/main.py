# Ensure DB models are imported before initializing DB so tables are created
import app.db.models  # register models with Base
from app.db.database import init_db

# create tables / run simple migrations
init_db()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, emergencies, users, ws  # add other routers as needed


app = FastAPI(title="Rapid Maternal API")

# CORS (allow frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(emergencies.router)
app.include_router(users.router)
app.include_router(ws.router)

