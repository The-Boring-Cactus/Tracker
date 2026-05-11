from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import Project, Workspace, User
from ..schemas.projects import ProjectCreate, Project as ProjectSchema
from .auth import get_current_user

router = APIRouter(prefix="/projects", tags=["Projects"])

@router.get("/workspace/{workspace_id}", response_model=List[ProjectSchema])
def get_projects(workspace_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    projects = db.query(Project).filter(Project.workspace_id == workspace_id).all()
    return projects

@router.post("/", response_model=ProjectSchema)
def create_project(project: ProjectCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    workspace = db.query(Workspace).filter(Workspace.id == project.workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
        
    db_project = Project(**project.model_dump())
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

@router.get("/{project_id}", response_model=ProjectSchema)
def get_project(project_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.delete("/{project_id}")
def delete_project(project_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    db.delete(project)
    db.commit()
    return {"message": "Project deleted successfully"}
