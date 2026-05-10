from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from .routers import setup, auth, workspaces, projects, project_entities
from .database import engine, Base

app = FastAPI(title="Project Tracking API")

import os
os.makedirs("uploads/attachments", exist_ok=True)
app.mount("/static/attachments", StaticFiles(directory="uploads/attachments"), name="attachments")

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For dev, allow all. Change in production.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(setup.router)
app.include_router(auth.router)
app.include_router(workspaces.router)
app.include_router(projects.router)
app.include_router(project_entities.router)

@app.get("/")
def root():
    return {"message": "Welcome to Project Tracking API"}
