from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import Workspace, User
from ..schemas.workspaces import WorkspaceCreate, Workspace as WorkspaceSchema
from .auth import get_current_user

router = APIRouter(prefix="/workspaces", tags=["Workspaces"])

@router.get("/", response_model=List[WorkspaceSchema])
def get_workspaces(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # For now, returning all workspaces since there is no WorkspaceUser association
    # In a full implementation, you'd filter by user access
    workspaces = db.query(Workspace).all()
    return workspaces

@router.post("/", response_model=WorkspaceSchema)
def create_workspace(workspace: WorkspaceCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_workspace = Workspace(**workspace.model_dump())
    db.add(db_workspace)
    db.commit()
    db.refresh(db_workspace)
    return db_workspace

@router.get("/{workspace_id}", response_model=WorkspaceSchema)
def get_workspace(workspace_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    return workspace

@router.delete("/{workspace_id}")
def delete_workspace(workspace_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    db.delete(workspace)
    db.commit()
    return {"message": "Workspace deleted successfully"}
